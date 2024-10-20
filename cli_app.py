from exploit.restore import restore_files, FileToRestore
from devicemanagement.constants import Device
from pymobiledevice3 import usbmux
from pymobiledevice3.lockdown import create_using_usbmux
import plistlib
import traceback

running = True
device = None

language = "en"

default_disabled_plist = {
    "com.apple.magicswitchd.companion": True,
    "com.apple.security.otpaird": True,
    "com.apple.dhcp6d": True,
    "com.apple.bootpd": True,
    "com.apple.ftp-proxy-embedded": False,
    "com.apple.relevanced": True
}

language_pack = {
    "en": {
        "title": "Daemon Disabler",
        "modified_by": "Modified by rponeawa from LeminLimez's Nugget.\nringojuice made a re-modifiy based on rponeawa's work.",
        "backup_warning": "Please back up your device before using!",
        "connect_prompt": "Please connect your device and try again!",
        "connected": "Connected to",
        "ios_version": "iOS",
        "supported": "Supported",
        "not_supported": "Not Supported",
        "menu_options": [
            "[{check}] 1. Disable thermalmonitord",
            "[{check}] 2. Disable OTA",
            "[{check}] 3. Disable UsageTrackingAgent",
            "[{check}] 4. Disable spotlightknowledged (experimental)",
            "[{check}] 5. Disable MobileAccessoryUpdater (experimental) ",
            "6. Apply changes",
            "7. 切换到简体中文",
            "0. Exit"
        ],
        "apply_changes": "Applying changes to disabled.plist...",
        "success": "Changes applied successfully!",
        "error": "An error occurred while applying changes to disabled.plist:",
        "goodbye": "Goodbye!",
        "input_prompt": "Enter a number: "
    },
    "zh": {
        "title": "守护程序禁用工具",
        "modified_by": "由 rponeawa 基于 LeminLimez 的 Nugget 修改。\nringojuice 在 rponeawa 的基础上进行了再次修改。",
        "backup_warning": "使用前请备份您的设备！",
        "connect_prompt": "请连接设备并重试！",
        "connected": "已连接到",
        "ios_version": "iOS",
        "supported": "支持的版本",
        "not_supported": "不支持的版本",
        "menu_options": [
            "[{check}] 1. 禁用 thermalmonitord (热状态监测,禁用后热状态将始终为Normal,同时电池显示未知部件)",
            "[{check}] 2. 禁用系统更新",
            "[{check}] 3. 禁用 UsageTrackingAgent (使用状态追踪,禁用后将大幅缓解高负载状态下的卡顿情况)",
            "[{check}] 4. 禁用 spotlightknowledged (测试)",
            "[{check}] 5. 禁用 MobileAccessoryUpdater (测试)",
            "6. 应用更改",
            "7. Switch to English",
            "0. 退出"
        ],
        "apply_changes": "正在应用更改到 disabled.plist...",
        "success": "更改已成功应用！",
        "error": "应用更改时发生错误：",
        "goodbye": "再见！",
        "input_prompt": "请输入选项: "
    }
}

def modify_disabled_plist(add_thermalmonitord=False, add_ota=False, add_usage_tracking_agent=False, add_spotlightknowledged=False, add_mobileaccessoryupdater=False):
    plist = default_disabled_plist.copy()

    if add_thermalmonitord:
        plist["com.apple.thermalmonitord"] = True
    else:
        plist.pop("com.apple.thermalmonitord", None)

    if add_ota:
        plist["com.apple.mobile.softwareupdated"] = True
        plist["com.apple.OTATaskingAgent"] = True
        plist["com.apple.softwareupdateservicesd"] = True
    else:
        plist.pop("com.apple.mobile.softwareupdated", None)
        plist.pop("com.apple.OTATaskingAgent", None)
        plist.pop("com.apple.softwareupdateservicesd", None)

    if add_usage_tracking_agent:
        plist["com.apple.UsageTrackingAgent"] = True
    else:
        plist.pop("com.apple.UsageTrackingAgent", None)

    if add_spotlightknowledged:
        plist["com.apple.spotlightknowledged"] = True
    else:
        plist.pop("com.apple.spotlightknowledged", None)

    if add_mobileaccessoryupdater:
        plist["com.apple.accessoryupdater"] = True
        plist["com.apple.MobileAccessoryUpdater"] = True
    else:
        plist.pop("com.apple.accessoryupdater", None)
        plist.pop("com.apple.MobileAccessoryUpdater", None)

    plist_data = {'plist': {'dict': plist}}
    return plistlib.dumps(plist, fmt=plistlib.FMT_XML)

def print_menu(thermalmonitord, disable_ota, disable_usage_tracking_agent, disable_spotlightknowledged, disable_mobileaccessoryupdater):
    menu = language_pack[language]["menu_options"]
    for i, option in enumerate(menu):
        if i == 0:
            check = "✓" if thermalmonitord else "×"
        elif i == 1:
            check = "✓" if disable_ota else "×"
        elif i == 2:
            check = "✓" if disable_usage_tracking_agent else "×"
        elif i == 3:
            check = "✓" if disable_spotlightknowledged else "×"
        elif i == 4:
            check = "✓" if disable_mobileaccessoryupdater else "×"
        else:
            check = ""
        print(option.format(check=check))

while running:
    print(language_pack[language]["title"])
    print(language_pack[language]["modified_by"])
    print(language_pack[language]["backup_warning"] + "\n")

    while device is None:
        connected_devices = usbmux.list_devices()
        for current_device in connected_devices:
            if current_device.is_usb:
                try:
                    ld = create_using_usbmux(serial=current_device.serial)
                    vals = ld.all_values
                    device = Device(uuid=current_device.serial, name=vals['DeviceName'],
                                    version=vals['ProductVersion'],build=vals['BuildVersion'], model=vals['ProductType'],
                                    locale=ld.locale, ld=ld)
                except Exception as e:
                    print(traceback.format_exc())
                    input("Press Enter to continue...")

        if device is None:
            print(language_pack[language]["connect_prompt"])
            input("Press Enter to continue...")
    if device.supported():
        print(f"{language_pack[language]['connected']} {device.name}\n{language_pack[language]['ios_version']} {device.version} Build {device.build} ({language_pack[language]['supported']})\n")
    else:
        print(f"{language_pack[language]['connected']} {device.name}\n{language_pack[language]['ios_version']} {device.version} Build {device.build} ({language_pack[language]['not_supported']})\n")

    thermalmonitord = False
    disable_ota = False
    disable_usage_tracking_agent = False
    disable_spotlightknowledged = False
    disable_mobileaccessoryupdater = False

    while True:
        print_menu(thermalmonitord, disable_ota, disable_usage_tracking_agent, disable_spotlightknowledged, disable_mobileaccessoryupdater)
        choice = int(input(language_pack[language]["input_prompt"]))

        if choice == 1:
            thermalmonitord = not thermalmonitord
        elif choice == 2:
            disable_ota = not disable_ota
        elif choice == 3:
            disable_usage_tracking_agent = not disable_usage_tracking_agent
        elif choice == 4:
            disable_spotlightknowledged = not disable_spotlightknowledged
        elif choice == 5:
            disable_mobileaccessoryupdater = not disable_mobileaccessoryupdater
        elif choice == 6:
            try:
                print("\n" + language_pack[language]["apply_changes"])
                plist_data = modify_disabled_plist(
                    add_thermalmonitord=thermalmonitord,
                    add_ota=disable_ota,
                    add_usage_tracking_agent=disable_usage_tracking_agent,
                    add_spotlightknowledged=disable_spotlightknowledged,
                    add_mobileaccessoryupdater=disable_mobileaccessoryupdater
                )

                restore_files(files=[FileToRestore(
                    contents=plist_data,
                    restore_path="/var/db/com.apple.xpc.launchd/",
                    restore_name="disabled.plist"
                )], reboot=True, lockdown_client=device.ld)
            except Exception as e:
                print(language_pack[language]["error"])
                print(traceback.format_exc())

            running = False
            break

        elif choice == 7:
            language = "zh" if language == "en" else "en"
            print()
            print(language_pack[language]["title"])
            print(language_pack[language]["modified_by"])
            print(language_pack[language]["backup_warning"] + "\n")
            if device.supported():
                print(f"{language_pack[language]['connected']} {device.name}\n{language_pack[language]['ios_version']} {device.version} Build {device.build} ({language_pack[language]['supported']})\n")
            else:
                print(f"{language_pack[language]['connected']} {device.name}\n{language_pack[language]['ios_version']} {device.version} Build {device.build} ({language_pack[language]['not_supported']})\n")
        elif choice == 0:
            print()
            print(language_pack[language]["goodbye"])
            running = False
            break

        print()