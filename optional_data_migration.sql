-- Optional: Migrate seller data from original database
-- Run this ONLY if you want to preserve existing seller information

USE chatbot_armaddia;

-- Migrate sellers (adjust field mapping as needed)
INSERT INTO sellers (name, email, phone, territory, status, created_at)
SELECT 
    seller_name as name,
    email,
    NULL as phone,  -- Add phone if available in original
    NULL as territory,  -- Add territory if available in original
    CASE 
        WHEN status = 'Online' THEN 'active'
        WHEN status = 'Offline' THEN 'inactive'
        ELSE 'active'
    END as status,
    created_at
FROM chatbot_gpscontrol.seller 
WHERE seller_name IS NOT NULL;

-- Optional: Migrate some recent conversations for analytics
-- (Only if you want conversation history)
INSERT INTO conversations (user_id, channel, message, response, intent, confidence, created_at, session_id)
SELECT 
    CONCAT('migrated_', chat_report_id) as user_id,
    'migrated' as channel,
    message,
    answer as response,
    intent,
    0.8 as confidence,  -- Default confidence for migrated data
    created_at,
    CONCAT('migration_', DATE(created_at)) as session_id
FROM chatbot_gpscontrol.conversation 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)  -- Last 30 days only
LIMIT 1000;  -- Limit to prevent overwhelming the new system

-- Show migration results
SELECT 'Sellers migrated:' as status, COUNT(*) as count FROM sellers WHERE created_at IS NOT NULL
UNION ALL
SELECT 'Conversations migrated:' as status, COUNT(*) as count FROM conversations WHERE channel = 'migrated';