import Google from "next-auth/providers/google";
import {NextAuthConfig} from "next-auth";

export default {
  providers: [
    Google({
      authorization: {
        params: {
          scope: "openid email profile https://www.googleapis.com/auth/calendar.events",
          prompt: "consent",
          access_type: "offline",
        }
      }
    })
  ],
  pages: {
    signIn: "/login",
  },
  callbacks: {
    async redirect({baseUrl}) {
      // Redirect to dashboard after sign-in
      return baseUrl
    },
    async authorized({request, auth}) {
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
    async jwt({token, account}) {
      // Save refresh token to JWT token when user signs in
      if (account) {
        console.log('=== Account data from Google ===');
        console.log(JSON.stringify(account, null, 2));
        console.log('refresh_token:', account.refresh_token);
        console.log('================================');
        token.refreshToken = account.refresh_token;
        token.accessToken = account.access_token;
        token.expiresAt = account.expires_at;
      }
      return token;
    },
    async session({session, token}) {
      if (session.user) {
        session.user.id = token.sub!;
      }
      // Add tokens to session if needed
      if (token.refreshToken) {
        session.refreshToken = token.refreshToken as string;
      }
      if (token.accessToken) {
        session.accessToken = token.accessToken as string;
      }
      return session
    },
  },
} satisfies NextAuthConfig