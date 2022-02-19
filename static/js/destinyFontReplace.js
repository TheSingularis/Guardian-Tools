window.onload = onLoad();

function onLoad() {
    replaceDestinySymbols();
}

function replaceDestinySymbols() {
    document.body.innerHTML = document.body.innerHTML
        //Elements
        .replaceAll('[Arc]', "")
        .replaceAll('[Void]', "")
        .replaceAll('[Solar]', "")
        .replaceAll('[Stasis]', "")
        //Abilities
        .replaceAll('[Melee]', "")
        //Primary
        .replaceAll('[Hand Cannon]', "")
        .replaceAll('[Auto Rifle]', "")
        .replaceAll('[Bow]', "")
        //Secondary
        .replaceAll('[Fusion Rifle]', "")
        .replaceAll('[Grenade Launcher]', "")
        .replaceAll('[Shotgun]', "")
        //Power
        .replaceAll('[Sword]', "")
        .replaceAll('[Linear Fusion Rifle]', "")
        .replaceAll('[Rocket Launcher]', "")
        //Unique
        .replaceAll('[Trace Rifle]', "");
}