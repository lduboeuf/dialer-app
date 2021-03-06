# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# Copyright 2013, 2014 Canonical
#
# This file is part of dialer-app.
#
# dialer-app is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.

"""Dialer app autopilot custom proxy objects."""

import logging

import ubuntuuitoolkit
import time

from address_book_app.address_book import _common
from address_book_app import address_book
from autopilot import exceptions as autopilot_exceptions


class MainView(ubuntuuitoolkit.MainView):
    def __init__(self, *args):
        super().__init__(*args)
        self.logger = logging.getLogger(__name__)

    @property
    def dialer_page(self):
        return self.wait_select_single(DialerPage, greeterMode=False)

    @property
    def live_call_page(self):
        # wait until we actually have the calls before returning the live call
        self.hasCalls.wait_for(True)
        return self.wait_select_single(LiveCall, active=True)

    @property
    def contacts_page(self):
        return self._get_page(ContactsPage, 'contactsPage')

    @property
    def contact_editor_page(self):
        return self._get_page(DialerContactEditorPage, 'contactEditorPage')

    @property
    def contact_view_page(self):
        return self._get_page(DialerContactViewPage, 'contactViewPage')

    def get_first_log(self):
        return self.wait_select_single(objectName="historyDelegate0")

    def _click_button(self, button):
        """Generic way to click a button"""
        self.visible.wait_for(True)
        button.visible.wait_for(True)
        self.pointing_device.click_object(button)
        return button

    def _long_press(self, obj):
        """long press on object because press_duration is not honored on touch
        see bug #1268782

        :parameter obj: the object to long press on
        """

        self.pointing_device.move_to_object(obj)
        self.pointing_device.press()
        time.sleep(3)
        self.pointing_device.release()

    def check_ussd_error_dialog_visible(self):
        """Check if ussd error dialog is visible"""
        dialog = None
        try:
            dialog = self.wait_select_single(objectName="ussdErrorDialog")
        except:
            # it is ok to fail in this case
            return False

        return dialog.visible

    def check_ussd_progress_dialog_visible(self):
        """Check if ussd progress dialog is visible"""
        dialog = None
        try:
            dialog = self.wait_select_single(
                objectName="ussdProgressDialog")
        except:
            # it is ok to fail in this case
            return False

        return dialog.visible

    def _get_page(self, page_type, page_name):
        page = self.wait_select_single(
            page_type, objectName=page_name, active=True)
        return page


class LiveCall(MainView):

    def get_elapsed_call_time(self):
        """Return the elapsed call time"""
        return self.wait_select_single(objectName='stopWatch').elapsed

    def _get_hangup_button(self):
        """Return the hangup button"""
        return self.wait_select_single(objectName='hangupButton')

    def _get_call_hold_button(self):
        """Return the call holding button"""
        return self.wait_select_single(objectName='callHoldButton')

    def _get_swap_calls_button(self):
        """Return the swap calls button"""
        return self._get_call_hold_button()

    def _get_new_call_button(self):
        return self.wait_select_single(objectName='newCallButton')

    def get_multi_call_display(self):
        """Return the multi call display panel"""
        return self.wait_select_single(objectName='multiCallDisplay')

    def get_multi_call_item_for_number(self, number):
        """Return the multi call display item for the given number"""
        return self.wait_select_single(objectName='callDelegate',
                                       phoneNumber=number)

    def click_hangup_button(self):
        """Click and return the hangup page"""
        return self._click_button(self._get_hangup_button())

    def click_call_hold_button(self):
        """Click the call holding button"""
        return self._click_button(self._get_call_hold_button())

    def click_swap_calls_button(self):
        """Click the swap calls button"""
        return self._click_button(self._get_swap_calls_button())

    def click_new_call_button(self):
        """Click the new call button"""
        return self._click_button(self._get_new_call_button())


class DialerPage(MainView):

    def reveal_bottom_edge_page(self):
        """Bring the bottom edge page to the screen"""
        try:
            start_x = (
                self.globalRect.x +
                (self.globalRect.width * 0.5))
            # Start swiping from the top of the component because after some
            # seconds it gets almost fully hidden. The center will be out of
            # view.
            start_y = self.globalRect.y + self.height - 3
            stop_y = start_y - (self.height * 0.7)
            self.pointing_device.drag(start_x, start_y, start_x, stop_y,
                                      rate=2)
            self.bottomEdgeCommitted.wait_for(True)
        except autopilot_exceptions.StateNotFoundError:
            self.logger.error('BottomEdge element not found.')
            raise

    def _get_keypad_entry(self):
        return self.wait_select_single("KeypadEntry")

    def _get_keypad_keys(self):
        return self.select_many("KeypadButton")

    def _get_keypad_key(self, number):
        buttons_dict = {
            "0": "buttonZero",
            "1": "buttonOne",
            "2": "buttonTwo",
            "3": "buttonThree",
            "4": "buttonFour",
            "5": "buttonFive",
            "6": "buttonSix",
            "7": "buttonSeven",
            "8": "buttonEight",
            "9": "buttonNine",
            "*": "buttonAsterisk",
            "#": "buttonHash",
        }
        return self.wait_select_single("KeypadButton",
                                       objectName=buttons_dict[number])

    def _get_erase_button(self):
        """Return the erase button"""
        return self.wait_select_single("CustomButton",
                                       objectName="eraseButton")

    def _get_call_button(self):
        """Return the call button"""
        return self.wait_select_single(objectName="callButton")

    def click_call_button(self):
        """Click and return the call button"""
        return self._click_button(self._get_call_button())

    def click_erase_button(self):
        """Click the erase button"""
        self._click_button(self._get_erase_button())

    def click_keypad_button(self, keypad_button):
        """click the keypad button

        :param keypad_button: the clicked keypad_button
        """
        self._click_button(keypad_button)

    def trigger_copy_and_paste(self):
        """Invoke the copy and paste popup"""
        self._long_press(self._get_keypad_entry())

    def trigger_select_all(self):
        """Trigger select all"""
        button = self.get_root_instance().wait_select_single(
                        'UCAbstractButton',
                        objectName="select_all_button")
        self._click_button(button)

    def trigger_copy(self):
        """Trigger copy"""
        button = self.get_root_instance().wait_select_single(
                         'UCAbstractButton',
                         objectName="copy_button")
        self._click_button(button)

    def trigger_paste(self):
        """Trigger paste"""
        button = self.get_root_instance().wait_select_single(
                          'UCAbstractButton',
                          objectName="paste_button")
        self._click_button(button)

    def trigger_cut(self):
        """Trigger cut"""
        button = self.get_root_instance().wait_select_single(
                          'UCAbstractButton',
                          objectName="cut_button")
        self._click_button(button)

    def dial_number(self, number, formattedNumber):
        """Dial given number (string) on the keypad and return keypad entry

        :param number: the number to dial
        """
        for digit in number:
            button = self._get_keypad_key(digit)
            self.click_keypad_button(button)

        entry = self._get_keypad_entry()
        entry.value.wait_for(formattedNumber)
        return entry

    def call_number(self, number, formattedNumber):
        """Dial number and call return call_button"""
        self.dial_number(number, formattedNumber)
        self.click_call_button()
        return self.get_root_instance().wait_select_single(LiveCall)

    def click_header_action(self, action):
        """Click the action 'action' on the header"""
        action = self.wait_select_single(objectName='%s_button' % action)
        self.pointing_device.click_object(action)

    def click_contacts_button(self):
        self.click_header_action('contacts')


class DialerContactViewPage(address_book.ContactViewPage):
    """Autopilot custom proxy object for DialerContactViewPage components."""

    def call_phone(self, index):
        phone_group = self.select_single(
            'ContactDetailGroupWithTypeView',
            objectName='phones')

        call_buttons = phone_group.select_many(
            "ActionButton",
            objectName="tel-contact")
        self.pointing_device.click_object(call_buttons[index])


class DialerContactEditorPage(address_book.ContactEditorPage):
    """Autopilot custom proxy object for DialerContactEditorPage components."""

    def click_action_button(self, action_name):
        actions = self.select_many(objectName='%s_button' % action_name)
        for action in actions:
            if action.enabled:
                self.pointing_device.click_object(action)
                return

        raise autopilot_exceptions.StateNotFoundError(action_name)

    def save(self):
        """
        Press the 'Save' button
        """
        self.click_action_button('save')


class ContactsPage(_common.PageWithHeader):
    """Autopilot custom proxy object for ContactsPage components."""

    def _click_button(self, button):
        """Generic way to click a button"""
        self.visible.wait_for(True)
        button.visible.wait_for(True)
        self.pointing_device.click_object(button)
        return button

    def _get_add_new_button(self):
        """Return the add-new button"""
        return self.wait_select_single('ContactListButtonDelegate',
                                       objectName='addNewButton')

    def click_add_new(self):
        self._click_button(self._get_add_new_button())

    def click_contact(self, index):
        contact_delegate = self._get_contact_delegate(index)
        self.pointing_device.click_object(contact_delegate)

    def open_contact(self, index):
        self.click_contact(index)
        return self.get_root_instance().select_single(
            DialerContactViewPage, objectName='contactViewPage')

    def _get_contact_delegate(self, index):
        contact_delegates = self._get_sorted_contact_delegates()
        return contact_delegates[index]

    def _get_sorted_contact_delegates(self):
        contact_delegates = self.select_many('ContactDelegate', visible=True)
        return sorted(
            contact_delegates, key=lambda delegate: delegate.globalRect.y)
