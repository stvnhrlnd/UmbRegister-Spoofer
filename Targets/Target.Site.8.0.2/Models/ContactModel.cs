using System.ComponentModel.DataAnnotations;

namespace Target.Site._8._0._2.Models
{
    public class ContactModel
    {
        [Required]
        public string Name { get; set; }

        [Required]
        [EmailAddress]
        public string Email { get; set; }

        [Required]
        public string Message { get; set; }
    }
}