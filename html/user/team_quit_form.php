<?php

require_once("util.inc");
require_once("login.inc");
require_once("team.inc");
db_init();
print_team_quit_form($HTTP_GET_VARS["id"]);

?>
