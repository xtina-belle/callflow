import {ObjectId} from 'mongodb';

interface TimeSlot {
  weekday: string
  start: string
  end: string
}

export interface MeetingRequest {
  _id: ObjectId;
  userId: ObjectId;

  // Who to contact
  clientName: string;
  clientPhone: string;
  clientEmail?: string;

  // When they'd like to meet (optional)
  available_slots?: TimeSlot[]

  // Free notes
  notes?: string;

  // Fill after you actually schedule
  scheduledStart?: Date;
  scheduledEnd?: Date;
  calendarEventId?: string; // ID from your calendar provider

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}
