"use client"

import type React from "react"

import {useState} from "react"
import {Button} from "@/components/ui/button"
import {Input} from "@/components/ui/input"
import {Label} from "@/components/ui/label"
import {Textarea} from "@/components/ui/textarea"
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card"
import {toast} from "sonner"
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select";
import {Plus, X} from "lucide-react";

interface TimeSlot {
  weekday: string
  start: string
  end: string
}

const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

export function MeetingRequestForm() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    clientName: "",
    clientPhone: "",
    clientEmail: "",
    notes: "",
  })

  const [availableSlots, setAvailableSlots] = useState<TimeSlot[]>([])

  const addTimeSlot = () => {
    setAvailableSlots([...availableSlots, {weekday: "Mon", start: "09:00", end: "10:00"}])
  }

  const removeTimeSlot = (index: number) => {
    setAvailableSlots(availableSlots.filter((_, i) => i !== index))
  }

  const updateTimeSlot = (index: number, field: keyof TimeSlot, value: string) => {
    const newSlots = [...availableSlots]
    newSlots[index] = {...newSlots[index], [field]: value}
    setAvailableSlots(newSlots)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      const response = await fetch("/api/meeting-requests", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          ...formData,
          available_slots: availableSlots.length > 0 ? availableSlots : undefined,
        }),
      })

      if (!response.ok) throw new Error("Failed to create meeting request")

      toast.success("Meeting request created successfully")

      // Reset form
      setFormData({
        clientName: "",
        clientPhone: "",
        clientEmail: "",
        notes: "",
      })
      setAvailableSlots([])

      // Trigger refresh of the list
      window.dispatchEvent(new CustomEvent("meeting-request-created"))
    } catch {
      toast.error("Failed to create meeting request")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>New Meeting Request</CardTitle>
        <CardDescription>Fill out the form to create a new meeting request</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="clientName">Client Name *</Label>
              <Input
                id="clientName"
                required
                value={formData.clientName}
                onChange={(e) => setFormData({...formData, clientName: e.target.value})}
                placeholder="John Doe"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="clientPhone">Client Phone *</Label>
              <Input
                id="clientPhone"
                type="tel"
                required
                value={formData.clientPhone}
                onChange={(e) => setFormData({...formData, clientPhone: e.target.value})}
                placeholder="+1 (555) 123-4567"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="clientEmail">Client Email</Label>
              <Input
                id="clientEmail"
                type="email"
                value={formData.clientEmail}
                onChange={(e) => setFormData({...formData, clientEmail: e.target.value})}
                placeholder="john@example.com"
              />
            </div>
          </div>


          <div className="border-t pt-4">
            <div className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label>Available Time Slots</Label>
                  <Button type="button" variant="outline" size="sm" onClick={addTimeSlot}>
                    <Plus className="mr-2 h-4 w-4"/>
                    Add Slot
                  </Button>
                </div>

                {availableSlots.length > 0 && (
                  <div className="space-y-3">
                    {availableSlots.map((slot, index) => (
                      <div key={index} className="flex items-end gap-2 rounded-lg border bg-muted/50 p-3">
                        <div className="flex-1 space-y-2">
                          <Label className="text-xs">Weekday</Label>
                          <Select
                            value={slot.weekday}
                            onValueChange={(value) => updateTimeSlot(index, "weekday", value)}
                          >
                            <SelectTrigger>
                              <SelectValue/>
                            </SelectTrigger>
                            <SelectContent>
                              {WEEKDAYS.map((day) => (
                                <SelectItem key={day} value={day}>
                                  {day}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>

                        <div className="flex-1 space-y-2">
                          <Label className="text-xs">Start Time</Label>
                          <Input
                            type="time"
                            value={slot.start}
                            onChange={(e) => updateTimeSlot(index, "start", e.target.value)}
                          />
                        </div>

                        <div className="flex-1 space-y-2">
                          <Label className="text-xs">End Time</Label>
                          <Input
                            type="time"
                            value={slot.end}
                            onChange={(e) => updateTimeSlot(index, "end", e.target.value)}
                          />
                        </div>

                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={() => removeTimeSlot(index)}
                          className="h-10 w-10 text-muted-foreground hover:text-destructive"
                        >
                          <X className="h-4 w-4"/>
                          <span className="sr-only">Remove slot</span>
                        </Button>
                      </div>
                    ))}
                  </div>
                )}

                {availableSlots.length === 0 && (
                  <p className="text-sm text-muted-foreground">
                    No time slots added yet. Click 'Add Slot' to specify available times.
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({...formData, notes: e.target.value})}
                  placeholder="Additional information about the meeting..."
                  rows={4}
                />
              </div>
            </div>
          </div>

          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? "Creating..." : "Create Meeting Request"}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
