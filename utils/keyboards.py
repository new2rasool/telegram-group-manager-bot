"""
Inline keyboard builder functions for UI management.
Provides utilities to construct and manage inline keyboards for Telegram bot interactions.
"""

from typing import List, Optional, Dict, Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class KeyboardBuilder:
    """
    Helper class to build inline keyboards for Telegram bot UI management.
    """

    def __init__(self):
        """Initialize an empty keyboard builder."""
        self.buttons: List[List[InlineKeyboardButton]] = []

    def add_button(
        self,
        text: str,
        callback_data: Optional[str] = None,
        url: Optional[str] = None,
        switch_inline_query: Optional[str] = None,
    ) -> "KeyboardBuilder":
        """
        Add a single button to the current row.

        Args:
            text: Button display text
            callback_data: Callback query data for button interaction
            url: URL to open when button is clicked
            switch_inline_query: Inline query to switch to

        Returns:
            KeyboardBuilder: Self for method chaining
        """
        button = InlineKeyboardButton(
            text=text,
            callback_data=callback_data,
            url=url,
            switch_inline_query=switch_inline_query,
        )
        if not self.buttons or len(self.buttons[-1]) > 0:
            self.buttons.append([])
        self.buttons[-1].append(button)
        return self

    def add_button_row(
        self,
        buttons_data: List[Dict[str, str]],
    ) -> "KeyboardBuilder":
        """
        Add multiple buttons in a single row.

        Args:
            buttons_data: List of button data dictionaries with keys:
                         'text', 'callback_data', 'url', 'switch_inline_query'

        Returns:
            KeyboardBuilder: Self for method chaining
        """
        row = []
        for btn_data in buttons_data:
            button = InlineKeyboardButton(
                text=btn_data.get("text", ""),
                callback_data=btn_data.get("callback_data"),
                url=btn_data.get("url"),
                switch_inline_query=btn_data.get("switch_inline_query"),
            )
            row.append(button)
        if row:
            self.buttons.append(row)
        return self

    def row(self) -> "KeyboardBuilder":
        """
        Start a new row for button placement.

        Returns:
            KeyboardBuilder: Self for method chaining
        """
        if self.buttons and len(self.buttons[-1]) > 0:
            self.buttons.append([])
        return self

    def build(self) -> InlineKeyboardMarkup:
        """
        Build and return the InlineKeyboardMarkup.

        Returns:
            InlineKeyboardMarkup: The constructed inline keyboard
        """
        return InlineKeyboardMarkup(inline_keyboard=self.buttons)

    def clear(self) -> "KeyboardBuilder":
        """
        Clear all buttons from the builder.

        Returns:
            KeyboardBuilder: Self for method chaining
        """
        self.buttons = []
        return self


def create_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Create the main menu keyboard.

    Returns:
        InlineKeyboardMarkup: Main menu keyboard
    """
    builder = KeyboardBuilder()
    builder.add_button("📊 Statistics", callback_data="main_stats")
    builder.row()
    builder.add_button("👥 Members", callback_data="main_members")
    builder.add_button("⚙️ Settings", callback_data="main_settings")
    builder.row()
    builder.add_button("❌ Close", callback_data="main_close")
    return builder.build()


def create_group_selection_keyboard(groups: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """
    Create a keyboard for group selection.

    Args:
        groups: List of group dictionaries with 'id' and 'name' keys

    Returns:
        InlineKeyboardMarkup: Group selection keyboard
    """
    builder = KeyboardBuilder()
    for group in groups:
        builder.add_button(
            text=group.get("name", "Unknown"),
            callback_data=f"group_{group.get('id', '')}",
        )
        builder.row()
    builder.add_button("⬅️ Back", callback_data="back_to_main")
    return builder.build()


def create_member_action_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """
    Create a keyboard for member actions.

    Args:
        user_id: The user ID to perform actions on

    Returns:
        InlineKeyboardMarkup: Member action keyboard
    """
    builder = KeyboardBuilder()
    builder.add_button("🚫 Kick", callback_data=f"kick_{user_id}")
    builder.add_button("🔇 Mute", callback_data=f"mute_{user_id}")
    builder.row()
    builder.add_button("📋 Info", callback_data=f"info_{user_id}")
    builder.add_button("⚠️ Warn", callback_data=f"warn_{user_id}")
    builder.row()
    builder.add_button("⬅️ Back", callback_data="back_to_members")
    return builder.build()


def create_confirmation_keyboard(
    action: str, confirm_callback: str, cancel_callback: str = "cancel"
) -> InlineKeyboardMarkup:
    """
    Create a confirmation keyboard for critical actions.

    Args:
        action: The action being confirmed (for display)
        confirm_callback: Callback data for confirmation button
        cancel_callback: Callback data for cancellation button

    Returns:
        InlineKeyboardMarkup: Confirmation keyboard
    """
    builder = KeyboardBuilder()
    builder.add_button("✅ Confirm", callback_data=confirm_callback)
    builder.add_button("❌ Cancel", callback_data=cancel_callback)
    return builder.build()


def create_pagination_keyboard(
    page: int, total_pages: int, base_callback: str
) -> InlineKeyboardMarkup:
    """
    Create a pagination keyboard for browsing multiple pages.

    Args:
        page: Current page number (1-indexed)
        total_pages: Total number of pages
        base_callback: Base callback data for pagination (will append _prev/_next)

    Returns:
        InlineKeyboardMarkup: Pagination keyboard
    """
    builder = KeyboardBuilder()

    buttons = []
    if page > 1:
        buttons.append(
            {
                "text": "⬅️ Previous",
                "callback_data": f"{base_callback}_prev",
            }
        )
    buttons.append(
        {
            "text": f"📄 {page}/{total_pages}",
            "callback_data": f"{base_callback}_info",
        }
    )
    if page < total_pages:
        buttons.append(
            {
                "text": "Next ➡️",
                "callback_data": f"{base_callback}_next",
            }
        )

    builder.add_button_row(buttons)
    return builder.build()


def create_settings_keyboard() -> InlineKeyboardMarkup:
    """
    Create a settings keyboard.

    Returns:
        InlineKeyboardMarkup: Settings keyboard
    """
    builder = KeyboardBuilder()
    builder.add_button("🔐 Permissions", callback_data="settings_permissions")
    builder.row()
    builder.add_button("📝 Messages", callback_data="settings_messages")
    builder.add_button("⏱️ Timers", callback_data="settings_timers")
    builder.row()
    builder.add_button("🎯 Rules", callback_data="settings_rules")
    builder.row()
    builder.add_button("⬅️ Back", callback_data="back_to_main")
    return builder.build()


def create_yes_no_keyboard(callback_prefix: str = "action") -> InlineKeyboardMarkup:
    """
    Create a simple yes/no keyboard.

    Args:
        callback_prefix: Prefix for callback data (will append _yes/_no)

    Returns:
        InlineKeyboardMarkup: Yes/No keyboard
    """
    builder = KeyboardBuilder()
    builder.add_button("✅ Yes", callback_data=f"{callback_prefix}_yes")
    builder.add_button("❌ No", callback_data=f"{callback_prefix}_no")
    return builder.build()


def create_back_button(callback_data: str = "back_to_main") -> InlineKeyboardMarkup:
    """
    Create a simple back button keyboard.

    Args:
        callback_data: Callback data for the back button

    Returns:
        InlineKeyboardMarkup: Back button keyboard
    """
    builder = KeyboardBuilder()
    builder.add_button("⬅️ Back", callback_data=callback_data)
    return builder.build()


def create_multi_action_keyboard(
    actions: List[Dict[str, str]],
    columns: int = 2,
) -> InlineKeyboardMarkup:
    """
    Create a keyboard with multiple custom actions arranged in columns.

    Args:
        actions: List of action dictionaries with keys 'text' and 'callback_data'
        columns: Number of columns for button arrangement

    Returns:
        InlineKeyboardMarkup: Multi-action keyboard
    """
    builder = KeyboardBuilder()
    for i, action in enumerate(actions):
        builder.add_button(
            text=action.get("text", ""),
            callback_data=action.get("callback_data", ""),
        )
        if (i + 1) % columns == 0:
            builder.row()
    return builder.build()
