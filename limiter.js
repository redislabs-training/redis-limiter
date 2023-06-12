#!js api_version=1.0 name=limiter

// import with:
// redis-cli -x TFUNCTION LOAD REPLACE < ./limiter.js

redis.registerKeySpaceTrigger("limiter", "api:", function(client, data){
    if (data.event == 'expired'){
        redis.log(JSON.stringify(data));
        redis.log("Expiration of a api-per-minute counter");
    }
});


redis.registerFunction('check_limits', function(client, token, threshold){
    const date = new Date();
    let token_minute = "api:" + token + ":" + date.getMinutes().toString()
    ops = client.call("INCR", token_minute) 
    client.call("EXPIRE", token_minute, "59")
    if (ops < threshold)
        return true;
    else {
        client.call("XADD", "exceeding", "*", token, Date.now().toString())
        return false;
    }
});


redis.registerStreamTrigger(
    "consumer", 
    "exceeding", 
    function(client, data) {
        redis.log(JSON.stringify(data, (key, value) =>
            typeof value === 'bigint'
                ? value.toString()
                : value 
        ));
    }, 
    {
        isStreamTrimmed: true,
        window: 3
    }
);