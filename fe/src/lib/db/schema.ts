import {ObjectId} from 'mongodb';

export interface MeetingRequest {
  _id: ObjectId;
  userId: ObjectId;

  // Who to contact
  clientName: string;
  clientPhone: string;
  clientEmail?: string;

  // When they'd like to meet (optional)
  preferredStart?: Date;

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
