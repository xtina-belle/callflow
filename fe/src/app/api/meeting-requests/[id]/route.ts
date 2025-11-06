import {type NextRequest, NextResponse} from "next/server";

import {auth} from "@/app/auth";
import {deleteMeetingRequest} from "@/lib/db/meetingRequestsDao";

export async function DELETE(
  request: NextRequest,
  {params}: { params: { id: string } }
) {
  try {
    const session = await auth();
    if (!session?.user?.id) {
      return new Response("Unauthorized", {status: 401});
    }

    const deleted = await deleteMeetingRequest(params.id, session.user.id);
    if (!deleted) {
      return new Response("Could not delete meeting request", {status: 401});
    }

    return NextResponse.json(null, {status: 200});
  } catch (error) {
    console.error("Failed to delete meeting request:", error);
    return NextResponse.json(
      {error: "Failed to delete meeting request"},
      {status: 500}
    );
  }
}