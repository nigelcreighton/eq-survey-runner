#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT="$( cd "$( dirname "${DIR}"/../../)" && pwd )"

cd "${DIR}"/.. || exit

DESIGN_SYSTEM_VERSION="3.0.2"

rm -rf /tmp/templates*
wget -O /tmp/templates.zip "https://github.com/ONSdigital/design-system/releases/download/$DESIGN_SYSTEM_VERSION/templates.zip"
unzip /tmp/templates.zip -d /tmp/templates
rm -rf app/templates/components
rm -rf app/templates/layout
mv /tmp/templates/templates/* app/templates/
