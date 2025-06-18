### Manual Test Cases

**Objective:** Verify the functionality of the modified "Share" button and the new "QR Code" button.

**Prerequisites:**
- The application is running.
- A session has been created or joined, so the in-session UI is visible.

**Test Case 1: Verify Share Icon Button**
1.  **Action:** Locate the "Share" icon button (it should display a share icon, not text).
2.  **Expected Result:** The button is visible and uses the `share.svg` icon.
3.  **Action:** Click the "Share" icon button.
4.  **Expected Result:** The session URL should be copied to the clipboard.
5.  **Action:** Paste the content from the clipboard into a text editor or a new browser tab.
6.  **Expected Result:** The pasted content should be the correct and complete URL of the current session.

**Test Case 2: Verify QR Code Icon Button and Display**
1.  **Action:** Locate the "QR Code" icon button (it should display a QR code icon).
2.  **Expected Result:** The button is visible next to the "Share" icon button and uses the `qrcode.svg` icon.
3.  **Action:** Click the "QR Code" icon button.
4.  **Expected Result:** A modal dialog should appear on the screen.
5.  **Modal Content Verification:**
    *   The modal should have a title like "Scan QR Code to Share Session".
    *   A QR code image should be visible within the modal.
6.  **Action:** Use a QR code scanning app (e.g., on a smartphone) to scan the displayed QR code.
7.  **Expected Result:** The QR code app should decode the QR code and show the same URL as the current session URL.
8.  **Action:** Close the modal (e.g., by clicking the close button or outside the modal).
9.  **Expected Result:** The modal should disappear.

**Test Case 3: Verify UI Layout and Styling**
1.  **Action:** Observe the "Share" and "QR Code" buttons.
2.  **Expected Result:**
    *   Both buttons should be icon-only.
    *   The icons should be clearly visible and appropriately sized (e.g., 24x24 pixels or similar).
    *   The buttons should be aligned on the same row, likely within a button group.
    *   There should be adequate spacing between the buttons and other UI elements.

**Test Case 4: Verify Functionality on Different Timers/Session States**
1.  **Action:** Create sessions with different timer types (Count-down, Count-up, Time-per-move).
2.  **Expected Result:** The "Share" and "QR Code" buttons should be present and functional in all session types after the session is created and the main interface is visible. Their behavior (copying the link, showing the QR code for the link) should remain consistent.
