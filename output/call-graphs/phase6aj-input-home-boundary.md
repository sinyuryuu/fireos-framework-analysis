AmazonInputManagerService.onStart
  -> publishBinderService(amazon_input)
  -> publishBinderService(amazon_keyevent)
  -> shell service_manager find denied (saved SELinux AVC)
  -> authorized Amazon caller only
      -> GET_KEYEVENTS / whitelist / foreground / key map
      -> input callback registry
      -> ARIA may observe HOME (keycode 3) to dismiss overlay
      -> no bounded resolver API or Fire Launcher component selection

setInputFilter
  -> validateInputFilterAccessPermission
  -> system/updated-system app OR FILTER_INPUT_EVENTS(signature|amazon)
  -> InputManagerService.registerSecondaryInputFilter

BootAfterSystemOTAReceiver (related Phase 6AG/6R item)
  -> protected system-server OTA lifecycle
  -> OOBE state / OobeHomeActivity side effect
  -> not manually replayed; not a shell HOME selector
