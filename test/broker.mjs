/* eslint-disable @typescript-eslint/explicit-module-boundary-types */
import Aedes from "aedes";
import { createServer } from "node:net";

function listen(port) {
  const aedes = new Aedes();
  const server = createServer(aedes.handle);
  server.listen(port, () => {
    console.log("MQTT broker listening on port ", port);
  });
  aedes.on("clientError", (client, err) => {
    console.log("clientError", client.id, err.message);
  });
  aedes.on("client", client => {
    console.log("client connected", client.id);
  });
  aedes.on("clientDisconnect", client => {
    console.log("client disconnected", client.id);
  });
  aedes.on("subscribe", (subscriptions, client) => {
    console.log("subscribe from client", subscriptions, client.id);
  });

  // 用来伪造
  aedes.subscribe(
    // topic 需要全文匹配，123 是我们伪造的 session_id
    "session/123",
    (packet, callback) => {
      const payload = JSON.parse(packet.payload.toString());
      const returnTopic = `inputs/${payload.session_id}/${payload.job_id}`;
      console.log(`make fake response to session topic for ${returnTopic}`);
      aedes.publish({
        topic: returnTopic,
        payload: packet.payload,
      });
      callback();
    },
    () => {
      console.log("Subscribed to session topic");
    }
  );

  aedes.subscribe(
    "#",
    (packet, callback) => {
      if (!packet.topic.startsWith("$SYS")) {
        console.log(
          "date:",
          new Date().toLocaleString(),
          "topic:",
          packet.topic,
          "cmd:",
          packet.cmd,
          "payload:",
          packet.payload.toString()
        );
      }
      callback();
    },
    () => {
      console.log("Subscribed to all topics");
    }
  );
  return () =>
    new Promise((resolve, reject) =>
      server.close(err => (err ? resolve() : reject(err)))
    );
}


listen(47688)