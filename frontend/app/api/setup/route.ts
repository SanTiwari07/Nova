import { NextResponse } from 'next/server';

/**
 * DEPRECATED: Fallback asset generation removed per Household Autopilot specification.
 * The application strictly relies on genuine commerce catalog imagery from Swiggy Instamart,
 * with neutral 'Image unavailable' state when unverified.
 */
export async function GET() {
  return NextResponse.json({
    status: "deprecated",
    message: "Synthetic fallback generation is disabled. Real Swiggy catalog images or 'Image unavailable' state is used."
  });
}
