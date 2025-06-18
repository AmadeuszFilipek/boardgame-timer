import json
import random
import time

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods
import django.conf.global_settings as settings # Used for STATIC_URL, can be removed if favicon is handled differently

from game_sessions.models import GameSession, Player
from boardgame_timer.timer import CountDownTimer, CountUpTimer, TimePerMoveTimer

supported_timers = {
    'CountDownTimer': CountDownTimer,
    'CountUpTimer': CountUpTimer,
    'TimePerMoveTimer': TimePerMoveTimer
}

# --- Helper Functions ---

def _get_timer_instance(timer_type_name, initial_duration, timer_state_json):
    """
    Reconstructs a timer instance from its type, initial duration, and stored state.
    """
    timer_class = supported_timers.get(timer_type_name)
    if not timer_class:
        raise ValueError(f"Unsupported timer type: {timer_type_name}")

    # Common state attributes
    is_running = timer_state_json.get('is_running', False)
    start_time = timer_state_json.get('start_time') # Stored as Unix timestamp

    if timer_class == TimePerMoveTimer:
        # TimePerMoveTimer specific state
        timer = timer_class(move_time=initial_duration)
    elif timer_class == CountDownTimer:
        elapsed_at_pause = timer_state_json.get('elapsed_at_pause', 0)
        timer = timer_class(duration=initial_duration)
        timer._elapsed_at_pause = elapsed_at_pause
    elif timer_class == CountUpTimer:
        elapsed_at_pause = timer_state_json.get('elapsed_at_pause', 0) # For consistency, though CountUpTimer might not use it
        timer = timer_class()
        timer._elapsed_at_pause = elapsed_at_pause # Store it if needed by a modified CountUpTimer
    else: # Default case or other timers
        timer = timer_class(duration=initial_duration)


    timer._is_running = is_running
    if start_time:
        timer._start_time = start_time # Restore start_time (Unix timestamp)

    return timer

def _player_to_dict(player_model, game_session_model):
    """
    Serializes a Player model instance to a dictionary, including current timer values.
    """
    timer_instance = _get_timer_instance(
        game_session_model.timer_type,
        game_session_model.seconds, # For CountDownTimer and TimePerMoveTimer, this is the initial duration/move_time
        player_model.timer_state
    )
    return {
        'name': player_model.name,
        'id': player_model.player_id,
        'time': timer_instance.time(),  # Current time from the timer object
        'ratio': timer_instance.ratio(), # Current ratio from the timer object
        # 'timer_state': player_model.timer_state # For debugging if needed
    }

def _game_session_to_dict(game_session_model):
    """
    Serializes a GameSession model instance and its related Player model instances.
    """
    # Order players by their player_id for consistent frontend display
    players_queryset = game_session_model.players.all().order_by('player_id')
    players_data = [_player_to_dict(p, game_session_model) for p in players_queryset]

    return {
        'slug': game_session_model.slug,
        'id': game_session_model.id, # pk of the GameSession
        'type': game_session_model.timer_type,
        'version': game_session_model.version,
        'players': players_data,
        'active': game_session_model.any_timer_active,
        'activePlayer': game_session_model.active_player_name,
        'autoPass': game_session_model.auto_pass, # Include auto_pass setting
        'initialSeconds': game_session_model.seconds # Include initial seconds for reference
    }

def _get_initial_timer_state(game_session_model):
    """
    Returns a dictionary representing the initial state for a player's timer.
    """
    initial_state = {
        'is_running': False,
        'start_time': None, # Unix timestamp
        'initial_duration': game_session_model.seconds, # Store the session's default seconds
    }
    if game_session_model.timer_type == 'CountDownTimer':
        initial_state['elapsed_at_pause'] = 0
    elif game_session_model.timer_type == 'CountUpTimer':
        initial_state['elapsed_at_pause'] = 0 # Or whatever is appropriate for CountUpTimer reset
    # TimePerMoveTimer doesn't need elapsed_at_pause in the same way, start_time and initial_duration (move_time) are key
    return initial_state

def _update_player_timer_state(player_model, timer_instance, game_session_model):
    """
    Updates the player_model's timer_state from the timer_instance.
    """
    new_state = {
        'is_running': timer_instance._is_running,
        'start_time': timer_instance._start_time, # Unix timestamp
        'initial_duration': game_session_model.seconds, # or timer_instance._initial_duration if it can change per player
    }
    if isinstance(timer_instance, CountDownTimer):
        new_state['elapsed_at_pause'] = timer_instance._elapsed_at_pause
    elif isinstance(timer_instance, CountUpTimer):
         new_state['elapsed_at_pause'] = getattr(timer_instance, '_elapsed_at_pause', 0)

    player_model.timer_state = new_state
    player_model.save()

# --- View Functions ---

def getFavicon(request): # Consider moving to urls.py staticfiles_redirect or similar
   return HttpResponseRedirect(settings.STATIC_URL + 'icons/favicon.ico') # Use STATIC_URL from settings

def index(request):
   return render(request, 'index.html')

@require_http_methods(["GET"])
def getSession(request, session_slug):
   game_session = get_object_or_404(GameSession, slug=session_slug)
   return JsonResponse(_game_session_to_dict(game_session))

@require_http_methods(["GET"])
def getSessionAndIndex(request, session_slug):
   game_session = get_object_or_404(GameSession, slug=session_slug)
   context = {'session': json.dumps(_game_session_to_dict(game_session))}
   return render(request, 'index.html', context)

@require_http_methods(["POST"])
def createSession(request):
   inc_data = json.loads(request.body)
   new_session_name = inc_data["slug"]
   timer_name = inc_data["timer"]
   auto_pass = inc_data["autoPass"]
   seconds = int(inc_data["seconds"])

   if GameSession.objects.filter(slug=new_session_name).exists():
      return JsonResponse({'status': 'error', 'message': 'Session name is currently taken.'}, status=409)

   if timer_name not in supported_timers:
      return JsonResponse({'status': 'error', 'message': 'Invalid timer type.'}, status=400)

   game_session = GameSession.objects.create(
      slug=new_session_name,
      timer_type=timer_name,
      seconds=seconds,
      auto_pass=auto_pass,
      version=time.time()
   )
   return JsonResponse({'status': 'ok', 'slug': game_session.slug})

@require_http_methods(["POST"])
def addPlayer(request, session_slug, player_name):
   game_session = get_object_or_404(GameSession, slug=session_slug)

   if game_session.players.filter(name=player_name).exists():
      return JsonResponse({'status': 'error', 'message': "Player already exists."}, status=409)

   new_player_id = game_session.players.count()
   initial_timer_state = _get_initial_timer_state(game_session)

   Player.objects.create(
      game_session=game_session,
      name=player_name,
      player_id=new_player_id,
      timer_state=initial_timer_state
   )

   if not game_session.active_player_name:
      game_session.active_player_name = player_name
   
   game_session.version = time.time()
   game_session.save()

   channel_layer = get_channel_layer()
   updated_state_dict = _game_session_to_dict(game_session)
   session_group_name = f'session_{game_session.slug}'
   async_to_sync(channel_layer.group_send)(
       session_group_name,
       {
           'type': 'send_game_state',
           'state': updated_state_dict
       }
   )
   return JsonResponse({'status': 'ok'})

@require_http_methods(["POST"])
def togglePlayer(request, session_slug, player_name):
    game_session = get_object_or_404(GameSession, slug=session_slug)
    player_to_toggle = get_object_or_404(Player, game_session=game_session, name=player_name)

    timer_to_toggle = _get_timer_instance(game_session.timer_type, game_session.seconds, player_to_toggle.timer_state)

    new_active_player_name = None
    any_timer_now_active = False

    if game_session.active_player_name == player_name: # Current player is being toggled (stopped or started)
        if timer_to_toggle._is_running:
            timer_to_toggle.stop()
            # active_player_name remains this player, but their timer is not running
            # any_timer_active might become false if no other timer is running (relevant for multi-timer modes not yet implemented)
            any_timer_now_active = False # Simplified: assumes only one timer active at a time for now
        else:
            timer_to_toggle.start()
            any_timer_now_active = True
        _update_player_timer_state(player_to_toggle, timer_to_toggle, game_session)
        new_active_player_name = player_name # Keep this player as active, just their timer state changed

    else: # A different player is being made active
        if game_session.active_player_name: # Stop the currently active player, if any
            currently_active_player = game_session.players.filter(name=game_session.active_player_name).first()
            if currently_active_player:
                active_timer = _get_timer_instance(game_session.timer_type, game_session.seconds, currently_active_player.timer_state)
                if active_timer._is_running: # Ensure it's running before stopping
                    active_timer.stop()
                    _update_player_timer_state(currently_active_player, active_timer, game_session)

        # Start the new player's timer
        timer_to_toggle.start()
        _update_player_timer_state(player_to_toggle, timer_to_toggle, game_session)
        new_active_player_name = player_name
        any_timer_now_active = True

    game_session.active_player_name = new_active_player_name
    game_session.any_timer_active = any_timer_now_active
    game_session.version = time.time()
    game_session.save()

    channel_layer = get_channel_layer()
    updated_state_dict = _game_session_to_dict(game_session)
    session_group_name = f'session_{game_session.slug}'
    async_to_sync(channel_layer.group_send)(
        session_group_name,
        {
            'type': 'send_game_state',
            'state': updated_state_dict
        }
    )
    return JsonResponse({'status': 'ok'})


@require_http_methods(["POST"])
def _change_active_player(game_session, new_active_player_model):
    """Helper to manage stopping old player and starting new one."""
    if game_session.active_player_name and game_session.active_player_name != new_active_player_model.name:
        old_active_player = game_session.players.filter(name=game_session.active_player_name).first()
        if old_active_player:
            old_timer = _get_timer_instance(game_session.timer_type, game_session.seconds, old_active_player.timer_state)
            if old_timer._is_running:
                old_timer.stop()
                _update_player_timer_state(old_active_player, old_timer, game_session)

    new_timer = _get_timer_instance(game_session.timer_type, game_session.seconds, new_active_player_model.timer_state)
    if not new_timer._is_running: # Start only if not already running (e.g. from a direct toggle)
        new_timer.start()
        _update_player_timer_state(new_active_player_model, new_timer, game_session)

    game_session.active_player_name = new_active_player_model.name
    game_session.any_timer_active = True # New player is now active
    game_session.version = time.time()
    game_session.save()

    channel_layer = get_channel_layer()
    updated_state_dict = _game_session_to_dict(game_session)
    session_group_name = f'session_{game_session.slug}'
    async_to_sync(channel_layer.group_send)(
        session_group_name,
        {
            'type': 'send_game_state',
            'state': updated_state_dict
        }
    )


@require_http_methods(["POST"])
def nextPlayer(request, session_slug):
    game_session = get_object_or_404(GameSession, slug=session_slug)
    players = list(game_session.players.all().order_by('player_id'))
    if not players:
        return JsonResponse({'status': 'error', 'message': 'No players in session.'}, status=400)

    current_active_player_name = game_session.active_player_name
    current_idx = -1
    if current_active_player_name:
        for i, p in enumerate(players):
            if p.name == current_active_player_name:
                current_idx = i
                break

    next_idx = (current_idx + 1) % len(players)
    new_active_player = players[next_idx]

    _change_active_player(game_session, new_active_player)
    # _change_active_player now sends the game state
    return JsonResponse(_game_session_to_dict(game_session))


@require_http_methods(["POST"])
def previousPlayer(request, session_slug):
    game_session = get_object_or_404(GameSession, slug=session_slug)
    players = list(game_session.players.all().order_by('player_id'))
    if not players:
        return JsonResponse({'status': 'error', 'message': 'No players in session.'}, status=400)

    current_active_player_name = game_session.active_player_name
    current_idx = 0 # Default to first player if no active player (should ideally not happen if players exist)
    if current_active_player_name:
        for i, p in enumerate(players):
            if p.name == current_active_player_name:
                current_idx = i
                break

    prev_idx = (current_idx - 1 + len(players)) % len(players)
    new_active_player = players[prev_idx]

    _change_active_player(game_session, new_active_player)
    # _change_active_player now sends the game state
    return JsonResponse(_game_session_to_dict(game_session))


@require_http_methods(["POST"])
def start(request, session_slug): # Start current active player's timer
    game_session = get_object_or_404(GameSession, slug=session_slug)
    if not game_session.active_player_name:
        return JsonResponse({'status': 'error', 'message': 'No active player selected.'}, status=400)

    active_player = get_object_or_404(Player, game_session=game_session, name=game_session.active_player_name)
    timer = _get_timer_instance(game_session.timer_type, game_session.seconds, active_player.timer_state)

    if not timer._is_running:
        timer.start()
        _update_player_timer_state(active_player, timer, game_session)
        game_session.any_timer_active = True
        game_session.version = time.time()
        game_session.save()

        channel_layer = get_channel_layer()
        updated_state_dict = _game_session_to_dict(game_session)
        session_group_name = f'session_{game_session.slug}'
        async_to_sync(channel_layer.group_send)(
            session_group_name,
            {
                'type': 'send_game_state',
                'state': updated_state_dict
            }
        )
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'ok', 'message': 'Timer already running.'})


@require_http_methods(["POST"])
def stop(request, session_slug): # Stop current active player's timer
    game_session = get_object_or_404(GameSession, slug=session_slug)
    if not game_session.active_player_name:
        # If no active player, maybe stop all timers? For now, assume stop means current active player.
        return JsonResponse({'status': 'error', 'message': 'No active player selected to stop.'}, status=400)

    active_player = get_object_or_404(Player, game_session=game_session, name=game_session.active_player_name)
    timer = _get_timer_instance(game_session.timer_type, game_session.seconds, active_player.timer_state)

    if timer._is_running:
        timer.stop()
        _update_player_timer_state(active_player, timer, game_session)
        game_session.any_timer_active = False # Assuming only one timer active
        game_session.version = time.time()
        game_session.save()

        channel_layer = get_channel_layer()
        updated_state_dict = _game_session_to_dict(game_session)
        session_group_name = f'session_{game_session.slug}'
        async_to_sync(channel_layer.group_send)(
            session_group_name,
            {
                'type': 'send_game_state',
                'state': updated_state_dict
            }
        )
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'ok', 'message': 'Timer already stopped.'})


@require_http_methods(["POST"])
def restart(request, session_slug):
    game_session = get_object_or_404(GameSession, slug=session_slug)
    initial_timer_state = _get_initial_timer_state(game_session)

    for p in game_session.players.all():
        p.timer_state = initial_timer_state
        p.save()

    game_session.any_timer_active = False
    # game_session.active_player_name = None # Or reset to the first player? Current behavior is to keep active player.
    game_session.version = time.time()
    game_session.save()

    channel_layer = get_channel_layer()
    updated_state_dict = _game_session_to_dict(game_session)
    session_group_name = f'session_{game_session.slug}'
    async_to_sync(channel_layer.group_send)(
        session_group_name,
        {
            'type': 'send_game_state',
            'state': updated_state_dict
        }
    )
    return JsonResponse({'status': 'ok'})

@require_http_methods(["POST"])
def shufflePlayers(request, session_slug):
    game_session = get_object_or_404(GameSession, slug=session_slug)
    players = list(game_session.players.all())
    random.shuffle(players)

    for i, p_model in enumerate(players):
        p_model.player_id = i
        p_model.save()

    # Optionally, set active player to the new player at index 0 if desired
    # if players:
    #    game_session.active_player_name = players[0].name

    game_session.version = time.time()
    game_session.save()

    channel_layer = get_channel_layer()
    updated_state_dict = _game_session_to_dict(game_session)
    session_group_name = f'session_{game_session.slug}'
    async_to_sync(channel_layer.group_send)(
        session_group_name,
        {
            'type': 'send_game_state',
            'state': updated_state_dict
        }
    )
    return JsonResponse({'status': 'ok'})

@require_http_methods(["POST"])
def movePlayer(request, session_slug, player_name, new_placement_str):
    game_session = get_object_or_404(GameSession, slug=session_slug)
    player_to_move = get_object_or_404(Player, game_session=game_session, name=player_name)

    try:
        new_placement = int(new_placement_str) # new_placement is 0-indexed
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid placement value.'}, status=400)

    players = list(game_session.players.all().order_by('player_id'))

    if new_placement < 0 or new_placement >= len(players):
        return JsonResponse({'status': 'error', 'message': 'Placement out of bounds.'}, status=400)

    # Remove player from list
    original_idx = -1
    for i, p in enumerate(players):
        if p.id == player_to_move.id:
            original_idx = i
            break
    if original_idx != -1:
        players.pop(original_idx)

    # Insert player at new position
    players.insert(new_placement, player_to_move)

    # Re-assign player_ids
    for i, p_model in enumerate(players):
        p_model.player_id = i
        p_model.save()

    game_session.version = time.time()
    game_session.save()

    channel_layer = get_channel_layer()
    updated_state_dict = _game_session_to_dict(game_session)
    session_group_name = f'session_{game_session.slug}'
    async_to_sync(channel_layer.group_send)(
        session_group_name,
        {
            'type': 'send_game_state',
            'state': updated_state_dict
        }
    )
    return JsonResponse({'status': 'ok'})

# Note: Auto-pass logic (is_state_to_be_changed) is not implemented in GET requests (e.g., _game_session_to_dict).
# It should be handled by client-side logic triggering a specific view (e.g., nextPlayer) when a timer hits zero.
# The current implementation correctly saves and loads game_session.auto_pass.
