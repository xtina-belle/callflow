import NextAuth from "next-auth";

import authConfig from "@/app/auth.config";

export const { auth } = NextAuth(authConfig);

export default auth;

export const config = { matcher: ["/", "/login"] };
