window.onload = clear();

function clear() {
    //Elements
    document.body.innerHTML = document.body.innerHTML.replaceAll('[Arc]', "");
    document.body.innerHTML = document.body.innerHTML.replaceAll('[Void]', "");
    document.body.innerHTML = document.body.innerHTML.replaceAll('[Solar]', "");
    document.body.innerHTML = document.body.innerHTML.replaceAll('[Stasis]', "");

    //Abilities
    document.body.innerHTML = document.body.innerHTML.replaceAll('[Melee]', "");


    //Primary
    document.body.innerHTML = document.body.innerHTML.replaceAll('[Hand Cannon]', "");
    document.body.innerHTML = document.body.innerHTML.replaceAll('[Auto Rifle]', "");
    document.body.innerHTML = document.body.innerHTML.replaceAll('[Bow]', "");

    //Secondary
    document.body.innerHTML = document.body.innerHTML.replaceAll('[Fusion Rifle]', "");
    document.body.innerHTML = document.body.innerHTML.replaceAll('[Grenade Launcher]', "");
    document.body.innerHTML = document.body.innerHTML.replaceAll('[Shotgun]', "");

    //Power
    document.body.innerHTML = document.body.innerHTML.replaceAll('[Sword]', "");
    document.body.innerHTML = document.body.innerHTML.replaceAll('[Linear Fusion Rifle]', "");
    document.body.innerHTML = document.body.innerHTML.replaceAll('[Rocket Launcher]', "");

    //document.body.innerHTML = document.body.innerHTML.replaceAll('[Grenade Launcher]', "");

}   
