-- Verify
SELECT CURRENT_ROLE(), CURRENT_WAREHOUSE();

use role accountadmin;
use warehouse compute_wh; -- back to cheap warehouse

-- permanent setup
SET current_user = (SELECT CURRENT_USER());
ALTER USER IDENTIFIER($current_user)
  SET DEFAULT_ROLE = ACCOUNTADMIN,
      DEFAULT_WAREHOUSE = COMPUTE_WH;

----------- Resizing the DASH_WH_SI warehouse -----------
ALTER WAREHOUSE DASH_WH_SI
  SET WAREHOUSE_SIZE = 'XSMALL',
      AUTO_SUSPEND  = 60,
      AUTO_RESUME   = TRUE,
      MIN_CLUSTER_COUNT = 1,
      MAX_CLUSTER_COUNT = 1;

-- Stop it right now so it’s not burning credits
ALTER WAREHOUSE DASH_WH_SI SUSPEND;
---------------------------------------------------------


---------------------------------------------------------
-- If we wanna to activate it again
ALTER WAREHOUSE DASH_WH_SI RESUME;
---------------------------------------------------------


------------ If we want to work back using snowflake intelligence to (re)index or modify Cortex Search/Agents
USE ROLE SNOWFLAKE_INTELLIGENCE_ADMIN;
USE WAREHOUSE DASH_WH_SI;   -- does auto-resume
-- ...do the work...
ALTER WAREHOUSE DASH_WH_SI SUSPEND;  -- put it back to sleep
USE ROLE ACCOUNTADMIN;
USE WAREHOUSE COMPUTE_WH;
---------------------------------------------------------

SHOW WAREHOUSES LIKE 'DASH_WH_SI';

ALTER WAREHOUSE "DASH_WH_SI"
  SET AUTO_SUSPEND = 600
      AUTO_RESUME = TRUE;

----- Change it back
ALTER WAREHOUSE "DASH_WH_SI"
  SET AUTO_SUSPEND = 10
      AUTO_RESUME = FALSE;

---------------------------------------------------------