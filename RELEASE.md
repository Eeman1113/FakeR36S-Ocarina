Ocarina of Time (Ship of Harkinian) and Majora's Mask (2 Ship 2 Harkinian) for goodluckOS, as apps for the App Installer. The zips are the ports only, with nothing of the games in them: each one plays your own ROM.

**You need** a GA36-MB with a goodluckOS that has the App Installer (System Settings > System > App Installer) and your ROM: for Ocarina of Time a version Ship of Harkinian takes (N64 1.0 to 1.2 or PAL, GameCube or Master Quest), for Majora's Mask the N64 USA version (1.0) or the GameCube USA one.

1. Copy `ShipOfHarkinian-*.zip` and/or `2Ship2Harkinian-*.zip` to the `apps` folder of the console's HOME (over USB, where the console shows up as a drive, or with the card in a card reader) and install them in the App Installer. They show up in the Games tab.
2. Copy your ROM to HOME, as a `.z64`, `.n64` or `.v64` file or a zip of one.
3. Open the game. The first time, it finds your ROM and makes its assets from it, in a window that shows how far it has got; then the game starts, and from then on it starts straight away.

Saves, settings and the assets made from your ROM stay in `HOME/.config/soh` and `HOME/.config/2ship`, apart from the apps: a newer zip updates a port the same way, and uninstalling one keeps them. A port installed by hand before (`HOME/ports/soh`, `HOME/ports/2ship`) hands its assets, settings and saves to the app on its first start, without the ROM. So far it has been tested on one console.

How it works, how to build it, and the credits: [README](https://github.com/alvesmaicon/glOSports-harbourmasters#readme).
