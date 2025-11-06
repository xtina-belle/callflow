"use client"

import {Calendar, Mail, Phone, Trash2} from "lucide-react"
import {toast} from "sonner"
import {useEffect, useState} from "react"

import {Badge} from "@/components/ui/badge"
import {Button} from "@/components/ui/button"
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card"

interface MeetingRequest {
  _id: string
  clientName: string
  clientPhone: string
  clientEmail?: string
  preferredStart?: string
  notes?: string
  scheduledStart?: string
  scheduledEnd?: string
  createdAt: string
}

export function MeetingRequestsList() {
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

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Meeting Requests</CardTitle>
          <CardDescription>Loading meeting requests...</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Meeting Requests</CardTitle>
        <CardDescription>
          {requests.length} meeting {requests.length === 1 ? "request" : "requests"}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {requests.length === 0 ? (
          <div className="py-8 text-center text-muted-foreground">No meeting requests yet. Create your first one!</div>
        ) : (
          <div className="space-y-4">
            {requests.map((request) => (
              <div key={request._id} className="rounded-lg border bg-card p-4 transition-colors hover:bg-accent/50">
                <div className="mb-3 flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-foreground">{request.clientName}</h3>
                  </div>
                  <div className="flex items-center gap-2">
                    {request.scheduledStart ? (
                      <Badge variant="default">Scheduled</Badge>
                    ) : (
                      <Badge variant="secondary">Pending</Badge>
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(request._id)}
                      className="h-8 w-8 text-muted-foreground hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4"/>
                      <span className="sr-only">Delete request</span>
                    </Button>

                  </div>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Phone className="h-4 w-4"/>
                    <span>{request.clientPhone}</span>
                  </div>

                  {request.clientEmail && (
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Mail className="h-4 w-4"/>
                      <span>{request.clientEmail}</span>
                    </div>
                  )}

                  {request.preferredStart && (
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Calendar className="h-4 w-4"/>
                      <span>Preferred: {new Date(request.preferredStart).toLocaleString()}</span>
                    </div>
                  )}

                  {request.scheduledStart && (
                    <div className="flex items-center gap-2 text-foreground">
                      <Calendar className="h-4 w-4"/>
                      <span className="font-medium">
                        Scheduled: {new Date(request.scheduledStart).toLocaleString()}
                      </span>
                    </div>
                  )}

                  {request.notes && (
                    <div className="mt-2 rounded bg-muted p-2 text-muted-foreground">{request.notes}</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
