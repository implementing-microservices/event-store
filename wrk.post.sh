#! /usr/bin/env bash

wrk -t10 -c100 -d10s -s wrk.lua http://0.0.0.0:5000/events/kukuu

