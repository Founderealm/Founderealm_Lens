<?php
require_once 'a.php';
use App\Service;
class Mu {
    public function run() { return strlen("x"); }
}
function helper() { return (new Mu())->run(); }
