*** Settings ***
Documentation    Common keywords and setup for all IBM i task suites.

*** Keywords ***
Setup Standard Session
    [Arguments]    ${host}=pub400.com
    Initialize Connection    host=${host}
    Verify Positional Text    text=Sign On    row=1    col=36
