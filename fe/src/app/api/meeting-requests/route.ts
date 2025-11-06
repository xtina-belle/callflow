import { type NextRequest, NextResponse } from "next/server";

import {auth} from "@/app/auth";
import {createMeetingRequest, getAllMeetingRequests} from "@/lib/db/meetingRequestsDao";
import {MeetingRequestResponse} from "@/app/api/meeting-requests/types";


export async function GET() {
  try {
    const session = await auth();
    if (!session?.user?.id) {
      return new Response("Unauthorized", {status: 401});
    }

    const meetingRequestsData = await getAllMeetingRequests(session.user.id);
    return NextResponse.json({meetingRequests: meetingRequestsData} satisfies MeetingRequestResponse);
  } catch (error) {
    console.error("Failed to fetch meeting requests:", error)
    return NextResponse.json({ error: "Failed to fetch meeting requests" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const session = await auth();
    if (!session?.user?.id) {
      return new Response("Unauthorized", { status: 401 });
    }

    const meetingRequestData = await request.json();
    const newMeetingRequest = await createMeetingRequest(
      {
        ...meetingRequestData,
        accountManagerName: session.user.name,
        accountManagerEmail: session.user.email,
      },
      session.user.id,
    );

    return NextResponse.json({meetingRequest: newMeetingRequest}, {status: 201});
  } catch (error) {
    console.error("Failed to create meeting request:", error);
    return NextResponse.json(
      {error: "Failed to create meeting request"},
      {status: 500}
    );
  }
}

