#!js api_version=1.0 name=limiter

// import with:
// redis-cli -x TFUNCTION LOAD REPLACE < ./limiter.js

redis.registerKeySpaceTrigger("limiter", "api:", function(client, data){
    if ((data.event == 'incrby') || (data.event == 'incr')){

        // log the event
        redis.log(JSON.stringify(data));

        // get the token identifier
        const tokenApi = data.key.split(":").slice(0, -1).join(":");

        // build the Hash name, e.g.: {api:5I68T5910K}:data
        // the use of curly brackets is to co-locate the data with the counter
        const tokenApiData = `{${tokenApi}}:data`;

        // get the current timestamp
        var curr_time = client.call("time")[0];

        // add data to the Hash
        client.call('hset', tokenApiData, 'last', curr_time);
        client.call('hincrby', tokenApiData, 'ops', '1');
    }
}); 