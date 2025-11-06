import NextAuth from "next-auth";
import {MongoDBAdapter} from "@auth/mongodb-adapter";

import authConfig from "@/app/auth.config";
import {client} from "@/lib/db/db";

export const {handlers, signIn, signOut, auth} = NextAuth({
  ...authConfig,
  adapter: MongoDBAdapter(client),
  session: {strategy: "jwt"},
})
