import {ObjectId} from "mongodb";

import {db} from "@/lib/db/db";
import {MeetingRequest} from "@/lib/db/schema";

const COLLECTION = "meeting_requests";

export const getAllMeetingRequests = async (userId: string): Promise<MeetingRequest[]> => {
  return await db.collection<MeetingRequest>(COLLECTION)
    .find({userId: new ObjectId(userId)})
    .sort({createdAt: -1})
    .toArray();
};

export const createMeetingRequest = async (
  data, userId: string
): Promise<MeetingRequest> => {
  const collection = db.collection<MeetingRequest>(COLLECTION)

  const now = new Date();
  const meetingRequestData = {
    ...data,
    userId: new ObjectId(userId),
    _id: new ObjectId(),
    createdAt: now,
    updatedAt: now,
  };

  const result = await collection.insertOne(meetingRequestData);
  if (!result.acknowledged) {
    throw new Error('Failed to create meeting request');
  }

  return meetingRequestData;
};

export const deleteMeetingRequest = async (id: string, userId: string): Promise<MeetingRequest | null> => {
  const result = await db.collection<MeetingRequest>(COLLECTION).findOneAndDelete({
    _id: new ObjectId(id),
    userId: new ObjectId(userId),
  });
  return result || null;
};