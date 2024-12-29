import { EufyClean } from "./src";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

if (!process.env.EUFY_EMAIL || !process.env.EUFY_PASSWORD) {
  throw new Error("EUFY_EMAIL and EUFY_PASSWORD must be set in .env file");
}

const eufyClean = new EufyClean(
  process.env.EUFY_EMAIL,
  process.env.EUFY_PASSWORD
);

async function main() {
  await eufyClean.init();

  // Get all devices
  const devices = await eufyClean.getMqttDevices();
  console.log("Found devices:", devices);
}

main().catch(console.error);
