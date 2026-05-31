#!/bin/bash

EXPLAIN=false

if [[ "$1" == "explain" ]]; then
    EXPLAIN=true
fi

CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print 100 - $8}')
MEMORY=$(free | awk '/Mem:/ {printf("%.0f"), $3/$2 * 100}')
DISK=$(df / | awk 'END{print $5}' | sed 's/%//')

HEALTHY=true
REASON=""

if (( $(echo "$CPU > 60" | bc -l) )); then
    HEALTHY=false
    REASON+="CPU usage high ($CPU%). "
fi

if [ "$MEMORY" -gt 60 ]; then
    HEALTHY=false
    REASON+="Memory usage high ($MEMORY%). "
fi

if [ "$DISK" -gt 60 ]; then
    HEALTHY=false
    REASON+="Disk usage high ($DISK%). "
fi

if [ "$HEALTHY" = true ]; then
    STATUS="Healthy"
else
    STATUS="Not Healthy"
fi

echo "===================================="
echo " VM Health Check Report"
echo "===================================="
echo "Hostname      : $(hostname)"
echo "Checked At    : $(date)"
echo "CPU Usage     : $CPU%"
echo "Memory Usage  : $MEMORY%"
echo "Disk Usage    : $DISK%"
echo "Health Status : $STATUS"

if [ "$EXPLAIN" = true ]; then
    echo "Reason        : ${REASON:-All metrics are within threshold}"
fi

echo "===================================="