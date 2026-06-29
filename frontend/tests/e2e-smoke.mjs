import { chromium } from "playwright-core";

const browser = await chromium.launch({
  executablePath: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  headless: true,
});

const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const consoleErrors = [];
const failedRequests = [];
const badResponses = [];
const suffix = Date.now().toString().slice(-7);
const guardName = `Phase Nine Guard ${suffix}`;
const guardEmail = `phase9-${suffix}@example.com`;
const guardPassword = "Guard@123";
const plate = `P9-${suffix.slice(-5)}`;

page.on("console", (message) => {
  if (message.type() === "error") consoleErrors.push(message.text());
});
page.on("requestfailed", (request) => {
  failedRequests.push(`${request.method()} ${request.url()}: ${request.failure()?.errorText}`);
});
page.on("response", async (response) => {
  if (response.status() >= 400) {
    badResponses.push({
      status: response.status(),
      url: response.url(),
      body: await response.text().catch(() => ""),
    });
  }
});

async function login(email, password, expectedPath) {
  await page.goto("http://localhost:3000/login", { waitUntil: "networkidle" });
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.waitForURL(`**${expectedPath}`);
}

await login("admin@parkingmanagement.com", "Admin@123", "/dashboard");
await page.getByRole("heading", { name: /Welcome,/ }).waitFor();
await page
  .getByRole("navigation")
  .getByRole("link", { name: "Active Vehicles" })
  .click();
await page.waitForURL("**/parking/active");
await page.getByRole("heading", { name: "Active vehicles" }).waitFor();
await page.getByRole("navigation").getByRole("link", { name: "Guards" }).click();
await page.waitForURL("**/users");
await page.getByRole("heading", { name: "Guard accounts" }).waitFor();

await page.getByRole("button", { name: "Add guard" }).click();
await page.getByLabel("Name").fill(guardName);
await page.getByLabel("Email").fill(guardEmail);
await page.getByLabel("Password").fill(guardPassword);
await page.getByLabel("Phone").fill("+923001234567");
await page.getByRole("button", { name: "Create guard" }).click();
try {
  await page.getByRole("cell", { name: guardEmail }).waitFor();
} catch (error) {
  console.error(JSON.stringify({ badResponses, body: await page.locator("body").innerText() }));
  throw error;
}

await page.getByRole("button", { name: "Logout" }).click();
await page.waitForURL("**/login");
await login(guardEmail, guardPassword, "/parking/entry");
if (await page.getByRole("link", { name: "Guards" }).count()) {
  throw new Error("Guard navigation exposed the admin-only Guards link.");
}
await page.goto("http://localhost:3000/users");
await page.getByRole("heading", { name: "Access restricted" }).waitFor();
await page.getByRole("link", { name: "Return to vehicle entry" }).click();

await page.getByLabel("Plate number").fill(plate);
await page.getByLabel("Slot (optional)").fill("P9-A");
await page.getByRole("button", { name: "Create vehicle entry" }).click();
await page.getByText(`${plate} is now active.`).waitFor();
await page.getByRole("link", { name: "View active vehicles" }).click();
await page.getByPlaceholder("Search plate number").fill(plate);
const activeRow = page.getByRole("row").filter({ hasText: plate });
await activeRow.getByRole("link", { name: "Details" }).click();
await page.getByRole("heading", { name: plate }).waitFor();
if (await page.getByRole("button", { name: "Edit record" }).count()) {
  throw new Error("Guard could see an admin-only parking edit action.");
}
await page
  .getByRole("navigation")
  .getByRole("link", { name: "Active Vehicles" })
  .click();
await page.getByPlaceholder("Search plate number").fill(plate);
const exitRow = page.getByRole("row").filter({ hasText: plate });
await exitRow.getByRole("button", { name: "Complete exit" }).click();
await page.getByLabel("Cash payment received").check();
await page.getByRole("button", { name: "Complete and record payment" }).click();
await page.getByRole("heading", { name: "Exit completed" }).waitFor();
await page.getByRole("button", { name: "Done" }).click();

await page
  .getByRole("navigation")
  .getByRole("link", { name: "Search Parking" })
  .click();
await page.getByLabel("Plate number").fill(plate.toLowerCase().replace("-", ""));
await page.getByRole("button", { name: "Search" }).click();
await page.getByRole("row").filter({ hasText: plate }).waitFor();
await page
  .getByRole("navigation")
  .getByRole("link", { name: "Parking History" })
  .click();
await page.getByPlaceholder("Search plate").fill(plate);
await page.getByRole("row").filter({ hasText: plate }).waitFor();

await page.getByRole("button", { name: "Logout" }).click();
await page.waitForURL("**/login");
await login("admin@parkingmanagement.com", "Admin@123", "/dashboard");
await page.goto("http://localhost:3000/parking/history");
await page.getByPlaceholder("Search plate").fill(plate);
const historyRow = page.getByRole("row").filter({ hasText: plate });
await historyRow.getByRole("link", { name: "Manage" }).click();
await page.getByRole("dialog").waitFor();
await page.getByLabel("Notes").fill("Phase 9 browser verification");
await page.getByRole("button", { name: "Save changes" }).click();
await page.getByRole("button", { name: "Delete" }).click();
await page.getByRole("button", { name: "Delete record" }).click();
await page.waitForURL("**/parking/history");

await page.goto("http://localhost:3000/users");
const guardRow = page.getByRole("row").filter({ hasText: guardEmail });
await guardRow.getByRole("button", { name: `Delete ${guardName}` }).click();
await page.getByRole("button", { name: "Delete guard" }).click();
await page.screenshot({
  path: `${process.env.TEMP}\\phase9-users.png`,
  fullPage: true,
});

console.log(
  JSON.stringify({
    url: page.url(),
    title: await page.title(),
    hasAddGuard: await page.getByRole("button", { name: "Add guard" }).isVisible(),
    verifiedGuard: guardEmail,
    verifiedPlate: plate,
    consoleErrors,
    failedRequests,
    badResponses,
  }),
);

await browser.close();
