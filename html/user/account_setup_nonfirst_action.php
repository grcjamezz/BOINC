<?php

include_once("../inc/db.inc");
include_once("../inc/util.inc");
include_once("../inc/prefs.inc");

db_init();

$user = get_logged_in_user();

$prefs = prefs_parse_project($user->project_prefs);
prefs_resource_parse_form($prefs);
venue_parse_form($user);
project_prefs_update($user, $prefs);
venue_update($user);

Header("Location: account_setup_nonfirst_done.php");

?>
