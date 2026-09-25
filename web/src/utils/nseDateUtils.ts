/**
 * Utility for NSE Trading Window Date & Time Formatting
 * Enforces Indian Standard Time (IST, UTC+5:30) and valid NSE trading hours:
 * - Days: Monday to Friday
 * - Hours: 09:15 AM IST to 03:30 PM IST
 */

export function formatNSEDateTime(dateInput?: string | Date | null): string {
  if (!dateInput) return '—';

  let dateObj: Date;
  if (typeof dateInput === 'string') {
    // If ISO string lacks explicit timezone offset, treat as UTC
    const hasTZ = dateInput.endsWith('Z') || dateInput.includes('+') || (dateInput.includes('T') && dateInput.substring(dateInput.indexOf('T')).includes('-'));
    const str = hasTZ ? dateInput : `${dateInput}Z`;
    dateObj = new Date(str);
  } else {
    dateObj = new Date(dateInput);
  }

  if (isNaN(dateObj.getTime())) return '—';

  // Convert UTC timestamp to IST Date components (UTC + 5 hours 30 minutes)
  const istOffsetMs = 5.5 * 60 * 60 * 1000;
  const istDate = new Date(dateObj.getTime() + istOffsetMs);

  let year = istDate.getUTCFullYear();
  let month = istDate.getUTCMonth(); // 0-indexed (0-11)
  let day = istDate.getUTCDate();
  let hours = istDate.getUTCHours();
  let minutes = istDate.getUTCMinutes();
  let dayOfWeek = istDate.getUTCDay(); // 0 = Sun, 6 = Sat

  // 1. Weekend Adjustment (Saturday = 6, Sunday = 0) -> Shift to preceding Friday
  if (dayOfWeek === 6) {
    day -= 1; // Saturday -> Friday
  } else if (dayOfWeek === 0) {
    day -= 2; // Sunday -> Friday
  }

  // Handle month boundary if day <= 0
  if (day <= 0) {
    month -= 1;
    if (month < 0) {
      month = 11;
      year -= 1;
    }
    const daysInPrevMonth = new Date(Date.UTC(year, month + 1, 0)).getUTCDate();
    day += daysInPrevMonth;
  }

  // 2. NSE Trading Hours Enforcement (09:15 AM IST to 03:30 PM IST)
  // 9:15 AM = 555 minutes from midnight
  // 3:30 PM = 930 minutes from midnight
  const totalMinutes = hours * 60 + minutes;
  const marketOpenMinutes = 9 * 60 + 15;  // 555
  const marketCloseMinutes = 15 * 60 + 30; // 930

  let finalHours = hours;
  let finalMinutes = minutes;

  if (totalMinutes < marketOpenMinutes) {
    // Before Market Open (09:15 AM IST) -> Set to Market Open
    finalHours = 9;
    finalMinutes = 15;
  } else if (totalMinutes > marketCloseMinutes) {
    // After Market Close (03:30 PM IST) -> Set to Market Close
    finalHours = 15;
    finalMinutes = 30;
  }

  // Format Month Name
  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const formattedMonth = monthNames[month];
  const formattedDay = String(day).padStart(2, '0');

  // Format 12-Hour AM/PM
  const period = finalHours >= 12 ? 'PM' : 'AM';
  let hour12 = finalHours % 12;
  if (hour12 === 0) hour12 = 12;
  const formattedHour = String(hour12).padStart(2, '0');
  const formattedMin = String(finalMinutes).padStart(2, '0');

  return `${formattedDay} ${formattedMonth} ${year}, ${formattedHour}:${formattedMin} ${period} IST`;
}

/**
 * Helper to determine if a signal status has changed and return the relevant status timestamp & label.
 */
export function getSignalStatusMeta(decision: any, stock?: any) {
  const status = decision?.status || stock?.status || 'WAITING_FOR_ENTRY';
  const createdAt = decision?.generatedAt || decision?.createdAt || stock?.created_at || stock?.timestamp;

  let statusChangeTime: string | undefined = undefined;
  let statusLabel: string = 'Status Updated';

  if (status === 'ENTRY_TRIGGERED' || status === 'ACTIVE') {
    statusChangeTime = decision?.triggeredAt || decision?.updatedAt || decision?.validatedAt || stock?.triggered_at || stock?.updated_at;
    statusLabel = 'Triggered';
  } else if (status === 'TARGET_HIT') {
    statusChangeTime = decision?.closedAt || decision?.updatedAt || stock?.outcome_timestamp || stock?.updated_at;
    statusLabel = 'Target Hit';
  } else if (status === 'STOP_LOSS') {
    statusChangeTime = decision?.closedAt || decision?.updatedAt || stock?.outcome_timestamp || stock?.updated_at;
    statusLabel = 'Stop Loss Hit';
  } else if (status === 'EXPIRED') {
    statusChangeTime = decision?.closedAt || decision?.updatedAt || stock?.outcome_timestamp || stock?.updated_at;
    statusLabel = 'Expired';
  } else if (status === 'CANCELLED') {
    statusChangeTime = decision?.updatedAt || stock?.updated_at;
    statusLabel = 'Cancelled';
  } else if (decision?.updatedAt || stock?.updated_at) {
    statusChangeTime = decision?.updatedAt || stock?.updated_at;
    statusLabel = 'Status Updated';
  }

  // Check if status change time is valid and distinct from creation time
  let hasStatusChanged = false;
  if (statusChangeTime && status !== 'WAITING_FOR_ENTRY' && status !== 'GENERATED') {
    hasStatusChanged = true;
  } else if (statusChangeTime && createdAt) {
    const tCreate = new Date(createdAt).getTime();
    const tChange = new Date(statusChangeTime).getTime();
    if (!isNaN(tCreate) && !isNaN(tChange) && Math.abs(tChange - tCreate) > 60000) {
      hasStatusChanged = true;
    }
  }

  return {
    createdAt,
    hasStatusChanged,
    statusLabel,
    statusChangeTime
  };
}
