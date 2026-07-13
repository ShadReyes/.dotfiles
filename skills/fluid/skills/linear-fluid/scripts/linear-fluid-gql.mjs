#!/usr/bin/env node

import { runCli } from "../../linear-graphql/scripts/linear-gql-core.mjs";
import { FLUID_LINEAR_PROFILE } from "../config.mjs";

process.exitCode = await runCli({ lockedProfile: FLUID_LINEAR_PROFILE, forceEnvelope: true });
