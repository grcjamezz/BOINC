<?php
    require_once("db.inc");
    require_once("util.inc");
    require_once("login.inc");
    require_once("prefs.inc");

    db_init();

    $user = get_user_from_cookie();
    if ($user) {
        page_head("Preferences");
        $prefs = prefs_parse($user->prefs);
        echo "<table width=780><tr><td>";
        echo "<p>This page is where you can edit your preferences.  
            There are both preferences about when you want your
            client to start up and how much work should be buffered
            for it and how much disk space you want to allow
            this project to use.";
        echo "</td></tr></table>";

        print_prefs_display($prefs);
    } else {
        print_login_form();
    }
    echo "<p>\n";
    page_tail();

?>
