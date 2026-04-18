*** Settings ***
Documentation    Example Robot Framework suite for IBM i Login.
Library          framework.libraries.IBMiLibrary
Resource         resources/common.resource

*** Variables ***
${USER}          %{IBMI_USER=DEFAULTUSER}
${PASSWORD}      %{IBMI_PASSWORD=DEFAULTPASS}

*** Test Cases ***
Verify Initial Sign On Screen
    [Documentation]    Connects to the system and verifies positional indicators.
    Initialize Connection
    Verify Positional Text    text=Sign On    row=1    col=36
    Verify Positional Text    text=System    row=3    col=27

Execute System Login
    [Documentation]    Performs a standard login and submits.
    Login To System    user=${USER}    password=${PASSWORD}
    # Here we would typically verify the next screen (e.g. Main Menu)
    [Teardown]    Close Connection
