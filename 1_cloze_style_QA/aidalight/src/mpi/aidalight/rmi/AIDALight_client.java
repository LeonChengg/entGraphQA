package mpi.aidalight.rmi;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import mpi.aida.data.Entity;
import mpi.aida.data.Mention;

public class AIDALight_client {

	/**
	 * 
	 * @param text
	 *            - this is clean text.
	 * @param mentions:
	 *            set null if mentions are not annotated. In this case, StanfordNER
	 *            will be used to annotate the text.
	 * @throws RemoteException
	 */
	public static void disambiguate(String text, List<Mention> mentions, String host) throws RemoteException {
		if (host == null)
			host = "localhost"; // default
		// set up server
		AIDALightServer server = null;
		try {
			Registry registry = LocateRegistry.getRegistry(host, 52365);
			server = (AIDALightServer) registry.lookup("NEDServer_" + host);
		} catch (Exception e) {
			e.printStackTrace();
		}

		String command = "fullSettings"; // = key-words + 2-phase mapping +
											// domain

		Map<Mention, Entity> annotations = server.disambiguate(text, mentions, command);

		// do whatever here...
		for (Mention mention : annotations.keySet()) {
			String wikipediaEntityId = "http://en.wikipedia.org/wiki/" + annotations.get(mention).getName();
			System.out.println(mention.getMention() + "\t" + wikipediaEntityId);
		}
	}

	public static AIDALightServer getServer(String host) throws RemoteException {
		if (host == null)
			host = "localhost"; // default
		// set up server
		AIDALightServer server = null;
		try {
			Registry registry = LocateRegistry.getRegistry(host, 52365);
			server = (AIDALightServer) registry.lookup("NEDServer_" + host);
		} catch (Exception e) {
			e.printStackTrace();
		}

		return server;
	}

	static JsonParser jparser = new JsonParser();

	public static void linkNewsStories(String[] args) throws IOException {
		// "news_raw.json.txt"
		// entTowikiContent.json
		BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream(args[0]), "UTF-8"));

		BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(args[1]), "UTF-8"));

		PrintWriter op = new PrintWriter(bw);

		String line;

		int prevArticleId = -1;
		String currentStr = "";

		String command = "fullSettings"; // = key-words + 2-phase mapping +
		// domain
		long t0 = System.currentTimeMillis();
		int lid = 1;
		AIDALightServer server = getServer(null);

		while ((line = br.readLine()) != null) {
			if (line.contains("[main]")) {
				continue;
			}
			// System.out.println(line);
			JsonObject obj = jparser.parse(line).getAsJsonObject();
			int artId = obj.get("articleId").getAsInt();
			String s = obj.get("s").getAsString();
			if (artId == prevArticleId || prevArticleId == -1) {
				currentStr += "\n" + s;
			} else {
				// time to run
				try {
					JsonObject thisew = runOneString(currentStr, server, command, prevArticleId);
					op.println(thisew);
				} catch (Exception e) {
					// TODO: handle exception
				}

				currentStr = s;
			}

			prevArticleId = artId;
			if (lid % 100 == 0) {
				System.err.println("lid: " + lid + " " + (System.currentTimeMillis() - t0));
			}
			lid++;

			// if (lid > 100000) {
			// break;
			// }

		}
		try {
			JsonObject thisew = runOneString(currentStr, server, command, prevArticleId);
			op.println(thisew);
		} catch (Exception e) {

		}

		br.close();
		op.close();

		System.err.println("lid: " + lid + " " + (System.currentTimeMillis() - t0));

	}

	// sample line: species glands also have 11
	static void linkGbooksCorpus(String[] args) throws IOException {
		String fname = args[0];
		String oname = args[1];

		String command = "fullSettings"; // = key-words + 2-phase mapping +
		// domain
		AIDALightServer server = getServer(null);
		PrintStream op = new PrintStream(new File(oname));

		BufferedReader br = new BufferedReader(new FileReader(fname));
		String line = null;
		int lid = 1;
		while ((line = br.readLine()) != null) {
			String[] ss = line.split("\t");
			String sent = ss[0] + " " + ss[2] + " " + ss[1];

			// System.out.println(sent);
			JsonObject thisew = runOneString(sent, server, command, lid++);// We don't care about artId here
			// System.out.println(thisew);
			op.println(thisew);
		}

		br.close();
	}

	static JsonObject runOneString(String s, AIDALightServer server, String command, int artId) throws RemoteException {
		Map<Mention, Entity> annotations = server.disambiguate(s, null, command);

		// do whatever here...
		// System.out.println(s);
		HashMap<String, String> entToWiki = new HashMap<String, String>();
		ArrayList<String> ents = new ArrayList<String>();
		for (Mention mention : annotations.keySet()) {

			String ent = mention.getMention();
			String wiki = annotations.get(mention).getName();

			if (!entToWiki.containsKey(ent)) {
				ents.add(ent);
			}

			// if (entToWiki.containsKey(ent) &&
			// !entToWiki.get(ent).equals(wiki)) {
			// System.out.println("not equal: " + ent + " " + entToWiki.get(ent)
			// + " " + wiki);
			// }

			entToWiki.put(ent, wiki);

			// String wikipediaEntityId = "http://en.wikipedia.org/wiki/" +
			// annotations.get(mention).getName();
			// System.out.println(mention.getMention() + "\t" +
			// wikipediaEntityId);
		}

		JsonObject ret = new JsonObject();
		ret.addProperty("artId", artId);

		JsonArray ja = new JsonArray();
		for (String e : ents) {
			JsonObject ew = new JsonObject();
			ew.addProperty("e", e);
			ew.addProperty("w", entToWiki.get(e));
			ja.add(ew);
		}

		ret.add("ew", ja);
		return ret;

		// System.out.println();
	}

	public static void main(String args[]) throws Exception {
		if (args.length == 0) {
			args = new String[] { "news_raw.json.txt", "entTowikiContent.json" };
		}

		// linkGbooksCorpus(args);
		linkNewsStories(args);

		// if (1 == 1) {
		// linkNewsStories(args);
		// return;
		// }

		// Scanner sc = new Scanner(new File("in.txt"));
		//
		// String command = "fullSettings"; // = key-words + 2-phase mapping +
		// // domain
		// long t0 = System.currentTimeMillis();
		// int lid = 0;
		// AIDALightServer server = getServer(null);
		//
		// while (sc.hasNext()) {
		// String s = sc.nextLine();
		//
		// runOneString(s, server, command);
		//
		// if (lid % 100 == 0) {
		// System.err.println("lid: " + lid + " " + (System.currentTimeMillis()
		// - t0));
		// }
		// lid++;
		// }
		// sc.close();
		// AIDALight_client.disambiguate("With United, Beckham won the Premier
		// League title 6 times.", null, null);
	}
}
