using System.Web.Mvc;
using Target.Site._8._1._0.Models;
using Umbraco.Web.Mvc;

namespace Target.Site._8._1._0.Controllers
{
    public class ContactController : SurfaceController
    {
        [ChildActionOnly]
        public ActionResult ContactForm()
        {
            var model = new ContactModel();
            return PartialView("ContactForm", model);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public ActionResult HandleContact(ContactModel model)
        {
            if (!ModelState.IsValid)
            {
                return CurrentUmbracoPage();
            }

            TempData["HandleContactSuccess"] = true;

            return RedirectToCurrentUmbracoPage();
        }
    }
}