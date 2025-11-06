import Google from "next-auth/providers/google";
import {NextAuthConfig} from "next-auth";

export default {
  providers: [Google],
  pages: {
    signIn: "/login",
  },
  callbacks: {
    async redirect({ baseUrl }) {
      // Redirect to dashboard after sign-in
      return baseUrl
    },
    async authorized({ request, auth }){
      const isLoggedIn = !!auth?.user;

      if (request.nextUrl.pathname === '/api/auth/callback/google') {
        return true;
      }

      if (request.nextUrl.pathname.startsWith('/login')) {
        if (isLoggedIn) {
          return Response.redirect(new URL('/', request.nextUrl as unknown as URL));
        }
        return true;
      }

      return isLoggedIn;
    },
    async session({session, token}) {
      if (session.user) {
        session.user.id = token.sub!;
      }
      return session
    },
  },
} satisfies NextAuthConfig