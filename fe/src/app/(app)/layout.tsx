import React from "react";
import {LogOut} from "lucide-react";

import {auth, signOut} from "@/app/auth";
import {TooltipProvider} from "@/components/ui/tooltip";
import {DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger} from "@/components/ui/dropdown-menu";
import {Avatar, AvatarFallback, AvatarImage} from "@/components/ui/avatar";
import {Sidebar} from "@/app/(app)/side-bar";



export default async function Layout({
                                       children,
                                     }: Readonly<{
  children: React.ReactNode
}>) {
  const session = await auth();
  const user = session?.user;

  return (
    <TooltipProvider>
      <div className="flex min-h-screen">
        <Sidebar/>
        <div className="flex flex-col flex-1">
          {user && (
            <header className="sticky top-0 z-10 flex justify-end items-center px-6 h-16">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <div className="flex items-center gap-2 cursor-pointer">
                    <Avatar className="h-8 w-8 rounded-lg">
                      {user.image && < AvatarImage src={user.image} alt={user.name || ""}/>}
                      <AvatarFallback className="rounded-lg">CN</AvatarFallback>
                    </Avatar>
                    <div className="grid flex-1 text-left text-sm leading-tight">
                      <span className="truncate font-medium">{user.name || ""}</span>
                      <span className="truncate text-xs">{user.email || ""}</span>
                    </div>
                  </div>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  className="w-(--radix-dropdown-menu-trigger-width) rounded-lg"
                  align="end"
                  sideOffset={4}
                >
                  <DropdownMenuItem onClick={async () => {
                    "use server"
                    await signOut()
                  }}>
                    <LogOut/>
                    Log out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </header>
          )}
          <main className="pl-14">{children}</main>
        </div>
      </div>
    </TooltipProvider>
  )
}
