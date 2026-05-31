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

echo "VM Health Status: $STATUS"

if [ "$EXPLAIN" = true ]; then
    echo "Reason: ${REASON:-All metrics within threshold}"
fi
