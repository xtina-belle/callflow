"use client"

import Link from "next/link";
import React from "react";
import {CalendarDays} from "lucide-react";

export function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-10 hidden w-14 flex-col border-r bg-background sm:flex">
      <div className="flex flex-col items-center gap-4 px-2 sm:py-5">
        <div className="bg-primary text-primary-foreground flex size-8 items-center justify-center rounded-lg">
          <Link href="/" className="">
            <CalendarDays className="size-6"/>
          </Link>
        </div>
      </div>
    </aside>
  )
}