"use client";

import {toast} from "sonner"
import {useEffect, useState} from "react";

import {MeetingRequestForm} from "@/components/meeting-request-form"
import {MeetingRequest, MeetingRequestsList} from "@/components/meeting-requests-list"

export default function MeetingRequestsPage() {
  const [requests, setRequests] = useState<MeetingRequest[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchRequests = async () => {
    try {
      const response = await fetch("/api/meeting-requests")
      if (response.ok) {
        const data = await response.json()
        setRequests(data.meetingRequests)
      }
    } catch (error) {
      console.error("Failed to fetch meeting requests:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (meetingRequestId: string) => {
    setIsLoading(true)
    const response = await fetch(`/api/meeting-requests/${meetingRequestId}`, {
      method: "DELETE",
    })

    if (response.ok) {
      toast.success("Meeting request deleted successfully")
      await fetchRequests();
    } else {
      toast.error("Failed to delete meeting request")
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchRequests()
  }, [])

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">Meeting Requests</h1>
          <p className="mt-2 text-muted-foreground">Create and manage client meeting requests</p>
        </div>

        <div className="grid gap-8 lg:grid-cols-2">
          <div>
            <MeetingRequestForm onSubmit={fetchRequests} />
          </div>
          <div className="lg:col-span-1">
            <MeetingRequestsList requests={requests} isLoading={isLoading} handleDelete={handleDelete}/>
          </div>
        </div>
      </div>
    </div>
  )
}
