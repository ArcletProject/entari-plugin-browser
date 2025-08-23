from arclet.entari import plugin, MessageCreatedEvent, Session
from entari_plugin_browser import md2img
from satori import Image

disp = plugin.dispatch(MessageCreatedEvent)


@disp.on()
@plugin.model.inject("web.render/playwright")
async def _(sess: Session):
    await sess.send([Image.of(raw=await md2img(sess.content), mime="image/jpeg")])
