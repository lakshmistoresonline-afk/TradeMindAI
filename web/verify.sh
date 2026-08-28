#!/bin/bash
echo "Verifying TradeMind AI Web Integrity..."
npm run build
if [ $? -eq 0 ]; then
  echo "INTEGRITY CHECK PASSED."
else
  echo "INTEGRITY CHECK FAILED."
fi
