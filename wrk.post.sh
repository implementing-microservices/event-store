#! /usr/bin/env bash

wrk -t50 -c100 -d20s -s wrk.lua http://0.0.0.0:5000/events/kukuu

