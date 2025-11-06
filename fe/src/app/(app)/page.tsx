"use client";

import { MeetingRequestForm } from "@/components/meeting-request-form"
import { MeetingRequestsList } from "@/components/meeting-requests-list"

export default function MeetingRequestsPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">Meeting Requests</h1>
          <p className="mt-2 text-muted-foreground">Create and manage client meeting requests</p>
        </div>

        <div className="grid gap-8 lg:grid-cols-2">
          <div>
            <MeetingRequestForm />
          </div>
          <div className="lg:col-span-1">
            <MeetingRequestsList />
          </div>
        </div>
      </div>
    </div>
  )
}
