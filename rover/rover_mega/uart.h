// uart.h
#ifndef AEGIS_UART_H
#define AEGIS_UART_H
#include <Arduino.h>

void uart_do_command();   // reads Serial1, executes motor actions
void uart_send_telemetry(); // pulls 1s averages and prints

#endif