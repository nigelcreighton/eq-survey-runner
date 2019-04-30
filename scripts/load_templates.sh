#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "${DIR}"/.. || exit

DESIGN_SYSTEM_VERSION="4.0.0"

rm -rf /tmp/templates*
curl -L --url "https://github.com/ONSdigital/design-system/releases/download/$DESIGN_SYSTEM_VERSION/templates.zip" --output /tmp/templates.zip
unzip /tmp/templates.zip -d /tmp/templates
rm -rf app/templates/components
rm -rf app/templates/layout
mv /tmp/templates/templates/* app/templates/
rm -rf /tmp/templates*
