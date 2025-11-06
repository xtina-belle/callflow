import {MeetingRequest} from "@/lib/db/schema";

export interface MeetingRequestResponse {
  meetingRequests: MeetingRequest[]
}
