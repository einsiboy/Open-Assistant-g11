import { NextApiRequest, NextApiResponse } from 'next';
import { withoutRole } from "src/lib/auth";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import { getLanguageFromRequest } from "src/lib/languages";
import { getBackendUserCore } from "src/lib/users";

/**
 * Fetch references based on a query parameter.
 */
const handler = withoutRole("banned", async (req: NextApiRequest, res: NextApiResponse, token) => {
    if (req.method !== 'GET') {
        res.setHeader('Allow', ['GET']);
        return res.status(405).end(`Method ${req.method} Not Allowed`);
    }


    const { query } = req.query;

    console.log("nextJS references: query", query);

    if (!query || typeof query !== 'string') {
        return res.status(400).json({ error: 'Query parameter is required' });
    }

    const lang = getLanguageFromRequest(req);
    const user = await getBackendUserCore(token.sub);
    const oasstApiClient = createApiClientFromUser(user);

    try {
        const references = await oasstApiClient.fetchReferences(query, lang);
        console.log("nextJS references", references);
        res.status(200).json(references);
    } catch (err) {
        // console.error(`Error fetching references: ${err.message}`);
        res.status(500).json({ error: 'Failed to fetch references' });
    }
});

export default handler;
