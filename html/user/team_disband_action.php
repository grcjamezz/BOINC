<?php

    require_once("util.inc");
    require_once("team.inc");
    require_once("db.inc");

    db_init();
    $user = get_logged_in_user();

    $query = sprintf(
        "select * from team where id = %d",
        $_POST["id"]
    );
    $result = mysql_query($query);
    if ($result) {
        $team = mysql_fetch_object($result);
        mysql_free_result($result);
    }
    require_founder_login($user, $team);

    $query_team_table = sprintf(
        "delete from team where id = %d",
        $team->id
    );
    if ($team->nusers == 0) {
        $result_team_table = mysql_query($query_team_table);
    }            
    if ($result_team_table) {
        $team_name = $team->name;
        page_head("$team_name disbanded");
        echo "<h2>Disband Complete</h2>";
        echo "You have disbanded $team_name.";
    } else {
        page_head("Error");
        echo "Couldn't disband team - please try later.\n";
    }

    page_tail();

?>
